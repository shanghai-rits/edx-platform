"""
Extra views required for SSO
"""


from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.generic.base import View
from django.db import transaction
from social_core.utils import setting_name
from social_django.utils import load_backend, load_strategy, psa
from social_django.views import complete
from social_django.models import UserSocialAuth

from common.djangoapps import third_party_auth
from common.djangoapps.student.helpers import get_next_url_for_login_page, is_safe_login_or_logout_redirect
from common.djangoapps.student.models import UserProfile
from common.djangoapps.student.views import compose_and_send_activation_email
from common.djangoapps.third_party_auth import pipeline, provider

from .models import SAMLConfiguration, SAMLProviderConfig
from django.utils.translation import ugettext as _
from openedx.core.lib.api.authentication import (
    BearerAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from ratelimit.decorators import ratelimit 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import (status, viewsets, permissions, authentication)
from .sms import TencentSmsService, check_phone_exists, sms_code_verification
from .phone import Phone
import logging
from common.djangoapps.track import rudderstack
from common.djangoapps.student.models import UserExtension

URL_NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'
log = logging.getLogger(__name__)

def inactive_user_view(request):
    """
    A newly or recently registered user has completed the social auth pipeline.
    Their account is not yet activated, but we let them login since the third party auth
    provider is trusted to vouch for them. See details in pipeline.py.

    The reason this view exists is that if we don't define this as the
    SOCIAL_AUTH_INACTIVE_USER_URL, inactive users will get sent to LOGIN_ERROR_URL, which we
    don't want.

    If the third_party_provider.skip_email_verification is set then the user is activated
    and verification email is not sent
    """
    # 'next' may be set to '/account/finish_auth/.../' if this user needs to be auto-enrolled
    # in a course. Otherwise, just redirect them to the dashboard, which displays a message
    # about activating their account.
    user = request.user
    profile = UserProfile.objects.get(user=user)
    activated = user.is_active
    # If the user is registering via 3rd party auth, track which provider they use
    if third_party_auth.is_enabled() and pipeline.running(request):
        running_pipeline = pipeline.get(request)
        third_party_provider = provider.Registry.get_from_pipeline(running_pipeline)
        if third_party_provider.skip_email_verification and not activated:
            user.is_active = True
            user.save()
            activated = True
    if not activated:
        compose_and_send_activation_email(user, profile)

    request_params = request.GET
    redirect_to = request_params.get('next')

    if redirect_to and is_safe_login_or_logout_redirect(redirect_to=redirect_to, request_host=request.get_host(),
                                                        dot_client_id=request_params.get('client_id'),
                                                        require_https=request.is_secure()):
        return redirect(redirect_to)

    return redirect('dashboard')


def saml_metadata_view(request):
    """
    Get the Service Provider metadata for this edx-platform instance.
    You must send this XML to any Shibboleth Identity Provider that you wish to use.
    """
    idp_slug = request.GET.get('tpa_hint', None)
    saml_config = 'default'
    if idp_slug:
        idp = SAMLProviderConfig.current(idp_slug)
        if idp.saml_configuration:
            saml_config = idp.saml_configuration.slug
    if not SAMLConfiguration.is_enabled(request.site, saml_config):
        raise Http404
    complete_url = reverse('social:complete', args=("tpa-saml", ))
    if settings.APPEND_SLASH and not complete_url.endswith('/'):
        complete_url = complete_url + '/'  # Required for consistency
    saml_backend = load_backend(load_strategy(request), "tpa-saml", redirect_uri=complete_url)
    metadata, errors = saml_backend.generate_metadata_xml(idp_slug)

    if not errors:
        return HttpResponse(content=metadata, content_type='text/xml')
    return HttpResponseServerError(content=', '.join(errors))


@csrf_exempt
@psa(f'{URL_NAMESPACE}:complete')
def lti_login_and_complete_view(request, backend, *args, **kwargs):
    """This is a combination login/complete due to LTI being a one step login"""

    if request.method != 'POST':
        return HttpResponseNotAllowed('POST')

    request.backend.start()
    return complete(request, backend, *args, **kwargs)


def post_to_custom_auth_form(request):
    """
    Redirect to a custom login/register page.

    Since we can't do a redirect-to-POST, this view is used to pass SSO data from
    the third_party_auth pipeline to a custom login/register form (possibly on another server).
    """
    pipeline_data = request.session.pop('tpa_custom_auth_entry_data', None)
    if not pipeline_data:
        raise Http404
    # Verify the format of pipeline_data:
    data = {
        'post_url': pipeline_data['post_url'],
        # data: The provider info and user's name, email, etc. as base64 encoded JSON
        # It's base64 encoded because it's signed cryptographically and we don't want whitespace
        # or ordering issues affecting the hash/signature.
        'data': pipeline_data['data'],
        # The cryptographic hash of user_data:
        'hmac': pipeline_data['hmac'],
    }
    return render(request, 'third_party_auth/post_custom_auth_entry.html', data)


class IdPRedirectView(View):
    """
    Redirect to an IdP's login page if the IdP exists; otherwise, return a 404.

    Example usage:

        GET auth/idp_redirect/saml-default

    """
    def get(self, request, *args, **kwargs):  # lint-amnesty, pylint: disable=unused-argument
        """
        Return either a redirect to the login page of an identity provider that
        corresponds to the provider_slug keyword argument or a 404 if the
        provider_slug does not correspond to an identity provider.

        Args:
            request (HttpRequest)

        Keyword Args:
            provider_slug (str): a slug corresponding to a configured identity provider

        Returns:
            HttpResponse: 302 to a provider's login url if the provider_slug kwarg matches an identity provider
            HttpResponse: 404 if the provider_slug kwarg does not match an identity provider
        """
        # this gets the url to redirect to after login/registration/third_party_auth
        # it also handles checking the safety of the redirect url (next query parameter)
        # it checks against settings.LOGIN_REDIRECT_WHITELIST, so be sure to add the url
        # to this setting
        next_destination_url = get_next_url_for_login_page(request)

        try:
            url = pipeline.get_login_url(kwargs['provider_slug'], pipeline.AUTH_ENTRY_LOGIN, next_destination_url)
            return redirect(url)
        except ValueError:
            return HttpResponseNotFound()

def send_sms_analytics(request):
    phone = request.data.get('phone')
    if phone:
        rudderstack.track(
                user_id=phone,
                event_name='edx.bi.smscode.sent',
                properties={
                    'action': request.data.get('action')
                }
            )

@ensure_csrf_cookie
@ratelimit(
    key='openedx.core.djangoapps.util.ratelimit.request_post_phone',
    rate='1/m',
    method='POST',
)
@ratelimit(
    key='openedx.core.djangoapps.util.ratelimit.real_ip',
    rate='1/m',
    method='POST',
)
@api_view(['POST'])
def send_sms_code(request):
    should_be_rate_limited = getattr(request, 'limited', False)
    if should_be_rate_limited and not settings.TENCENT_SMS_LOCAL_TEST:
        return Response({"error_message": 'Too many attempts. Try again later.'}, status=status.HTTP_403_FORBIDDEN)

    phone = request.data.get('phone')
    action = request.data.get('action')
    if not phone:
        return Response({"error_message": "Phone number is empty"}, status=status.HTTP_400_BAD_REQUEST)
    if not action:
        return Response({"error_message": "Missing parameter action"}, status=status.HTTP_400_BAD_REQUEST)

    if settings.TENCENT_SMS_LOCAL_TEST:
        code = '133400'
        service = TencentSmsService(phone, code)
        session = request.session
        session["sms_code"] = code
        session["phone"] = phone
        session["action"] = action
        session["expires"] = service.create_expires(minutes=settings.SMS_CODE_EXPIRES)
        log.warning("Sms code for test case: <{}>".format(code))
        log.warning("Sms code sent to: <{}>".format(phone))
        send_sms_analytics(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        code = TencentSmsService.create_sms_code()
        service = TencentSmsService(phone, code)
        resp = service.send()
        if resp.get('SendStatusSet')[0].get('Code') == 'Ok':
            session = request.session
            session["sms_code"] = code
            session["phone"] = phone
            session["action"] = action
            session["expires"] = service.create_expires(minutes=settings.SMS_CODE_EXPIRES)
            log.info(resp)
            send_sms_analytics(request)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logging.exception(msg=resp)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SMSViewSet(viewsets.ViewSet):
    """
        **Use Cases**

            Get, post, patch are supported.

        **Example Requests**

            GET /api/v1/phone
            POST /api/v1/phone
            PATCH /api/v1/phone

       """
    authentication_classes = (
        OAuth2AuthenticationAllowInactiveUser, BearerAuthenticationAllowInactiveUser, JwtAuthentication
    )
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request):
        """
        GET /api/v1/phone
        """
        try:
            user_social_auth = UserSocialAuth.objects.get(provider='sms', user=request.user)
            phone = user_social_auth.extra_data.get('phone')
        except UserSocialAuth.DoesNotExist:
            phone = None
        return Response({"phone": phone, "success": True})

    def partial_update(self, request):
        """
        PATCH /api/v1/phone
        """
        phone = request.data.get('phone')
        sms_code = request.data.get('sms_code')
        session = request.session
        conflicts = sms_code_verification(phone=phone, sms_code=sms_code, action="modify", session=session)
        phone_exist = check_phone_exists(phone)
        if conflicts:
            conflict_messages = {
                "sms_code": _(
                    u"Incorrect verification sms code."
                ),
            }
            errors = {
                field: [{"user_message": conflict_messages[field]}]
                for field in conflicts
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        if phone_exist:
            conflict_messages = {
                "phone": _(
                    u"This phone number is in use."
                ),
            }
            errors = {
                field: [{"phone": conflict_messages[field]}]
                for field in conflicts
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                UserSocialAuth.objects.filter(user=request.user, provider='sms').delete()
                phone = Phone(phone)
                user_social_auth = UserSocialAuth.create_social_auth(
                    uid=phone.make_phone(), provider='sms', user=request.user)
                user_social_auth.set_extra_data({'phone': phone.fuzzy()})
                user = user_social_auth.user
                user.is_active = True
                user.save()
                phone = user_social_auth.extra_data.get('phone')
                return Response({"phone": phone})
        except Exception as e:
            log.exception(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def check_exists(self, request):
        """
        POST /api/v1/phone
        """
        phone = request.data.get('phone')
        if check_phone_exists(phone=phone):
            return Response({"success": True, "message": "Phone number exist", "exist": True})
        return Response({"success": True, "message": "Phone number is ok", "exist": False})
