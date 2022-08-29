""" Objects and utilities used to construct phone login forms."""

import json
import logging
import urllib

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from ratelimit.decorators import ratelimit

from common.djangoapps import third_party_auth
from common.djangoapps.edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api import accounts
from openedx.core.djangoapps.user_api.accounts.utils import (
    is_secondary_email_feature_enabled
)
from openedx.core.djangoapps.user_api.helpers import FormDescription
from openedx.core.djangoapps.user_authn.cookies import set_logged_in_cookies
from openedx.core.djangoapps.user_authn.toggles import should_redirect_to_authn_microfrontend
from openedx.core.djangoapps.user_authn.views.password_reset import get_password_reset_form
from openedx.core.djangoapps.user_authn.views.registration_form import RegistrationFormFactory
from openedx.core.djangoapps.user_authn.views.utils import third_party_auth_context
from openedx.core.djangoapps.user_authn.toggles import is_require_third_party_auth_enabled
from openedx.features.enterprise_support.api import enterprise_customer_for_request, enterprise_enabled
from openedx.features.enterprise_support.utils import (
    get_enterprise_slug_login_url,
    handle_enterprise_cookies_for_logistration,
    update_logistration_context_for_enterprise
)
from common.djangoapps.student.helpers import get_next_url_for_login_page
from common.djangoapps.third_party_auth import pipeline
from common.djangoapps.third_party_auth.decorators import xframe_allow_whitelisted
from common.djangoapps.util.password_policy_validators import DEFAULT_MAX_PASSWORD_LENGTH

log = logging.getLogger(__name__)

class PhoneLoginFormFactory:
    """
    Construct Phone Login forms and associated fields.
    """

    def _apply_third_party_auth_overrides(self, request, form_desc):
        """Modify the login form if the user has authenticated with a third-party provider.
        If a user has successfully authenticated with a third-party provider,
        and an email is associated with it then we fill in the email field with readonly property.
        Arguments:
            request (HttpRequest): The request for the registration form, used
                to determine if the user has successfully authenticated
                with a third-party provider.
            form_desc (FormDescription): The registration form description
        """
        if third_party_auth.is_enabled():
            running_pipeline = third_party_auth.pipeline.get(request)
            if running_pipeline:
                current_provider = third_party_auth.provider.Registry.get_from_pipeline(running_pipeline)
                if current_provider and enterprise_customer_for_request(request):
                    pipeline_kwargs = running_pipeline.get('kwargs')

                    # Details about the user sent back from the provider.
                    details = pipeline_kwargs.get('details')
                    email = details.get('email', '')

                    # override the email field.
                    form_desc.override_field_properties(
                        "email",
                        default=email,
                        restrictions={"readonly": "readonly"} if email else {
                            "min_length": accounts.EMAIL_MIN_LENGTH,
                            "max_length": accounts.EMAIL_MAX_LENGTH,
                        }
                    )


    def get_login_session_form(self, request):
        """Return a description of the login form.

        This decouples clients from the API definition:
        if the API decides to modify the form, clients won't need
        to be updated.

        See `user_api.helpers.FormDescription` for examples
        of the JSON-encoded form description.

        Returns:
            HttpResponse

        """
        form_desc = FormDescription("post", reverse("user_api_login_session", kwargs={'api_version': 'v2'}))
        self._apply_third_party_auth_overrides(request, form_desc)

        # Translators: This label appears above a field on the login form
        # meant to hold the user's phone number.
        phone_label = _("Phone")

        # Translators: These instructions appear on the login form, immediately
        # below a field meant to hold the user's phone number.
        phone_instructions = _("The phone number you used to register with {platform_name}").format(
            platform_name=configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
        )

        phone_placeholder = _("10010001000")

        form_desc.add_field(
            "phone",
            field_type="text",
            restrictions={
                'min_length': 11,
                'max_length': 11,
            },
            label=phone_label,
            instructions=phone_instructions,
            placeholder=phone_placeholder
        )

        # Translators: This label appears above a field on the login form
        # meant to hold the user's password.
        sms_code_label = _("SMS Code")

        form_desc.add_field(
            "sms_code",
            label=sms_code_label,
            field_type="text",
            restrictions={
                'min_length': 6,
                'max_length': 6,
            }
        )

        return form_desc