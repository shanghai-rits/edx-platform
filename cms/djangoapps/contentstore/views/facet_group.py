"""
Views related to facets and groups.
A facet is a classification system which divide courses into different categories.
A group is a category of a certain facet.
"""
from __future__ import absolute_import

import logging
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import Http404, HttpResponseForbidden, HttpResponseNotAllowed
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import LibraryLocator, LibraryUsageLocator
from organizations.api import ensure_organization
from organizations.exceptions import InvalidOrganizationException
from django.http import HttpResponse
from cms.djangoapps.contentstore.utils import reverse_facet_url
from django.shortcuts import redirect

from common.djangoapps.edxmako.shortcuts import render_to_response
from common.djangoapps.util.json_request import JsonResponse, JsonResponseBadRequest, expect_json

from common.djangoapps.facet.models import Facet, Group, FacetOfCourse, GroupOfLanguage

__all__ = ['facet_handler']

log = logging.getLogger(__name__)

FACETS_ENABLED = settings.FEATURES.get('ENABLE_FACETS', False)


@login_required
@ensure_csrf_cookie
@require_http_methods(('GET', 'POST'))
def facet_handler(request, facet_key_string=None):
    """
    RESTful interface to facet related functionality.
    """
    if not FACETS_ENABLED:
        log.exception("Attempted to use the facet API when the facets feature is disabled.")
        raise Http404

    if facet_key_string and request.method == 'GET':
        return _display_facet(facet_key_string, request)

    if facet_key_string and request.method == 'POST':
        return _edit_facet(facet_key_string, request)

    if request.method == 'POST':
        return _create_facet(request)

    return HttpResponse(
        json.dumps([{"facet": entry.facet,
                     "term": GroupOfLanguage.get_group(request.LANGUAGE_CODE, Group.objects.get(group=entry.group)),
                     "course": entry.course} for entry in FacetOfCourse.objects.all()])
    )


def _display_facet(facet_key_string, request):
    """
    Helper method for displaying a facet.
    """
    if not request.user.is_staff:
        log.exception(
            u"User %s tried to access facet %s without permission",
            request.user.username, str(facet_key_string)
        )
        raise PermissionDenied()

    if not Facet.objects.get(number=facet_key_string):
        return JsonResponse("The facet you are looking for does not exist.")

    return render_to_response('facet.html', {
        'context_facet': facet_key_string,
        'displayname': Facet.objects.get(number=facet_key_string).displayname,
        # 'items': Group.objects.filter(facet=facet_key_string).values_list('group', flat=True)
        'items': [group for group in Group.objects.filter(facet=facet_key_string)]
    })


def _edit_facet(facet_key_string, request):
    """
    Helper method for editing a facet.
    """
    delete_group = request.POST.get('delete_group')
    add_group = request.POST.get('add_group')
    if delete_group is not None:
        group = Group.objects.filter(facet=facet_key_string, group=delete_group)[0]
        GroupOfLanguage.objects.filter(group=group).delete()
        Group.objects.filter(facet=facet_key_string, group=delete_group).delete()
        FacetOfCourse.objects.filter(facet=facet_key_string, group=delete_group).delete()
    elif add_group:
        if add_group not in Group.objects.filter(facet=facet_key_string).values_list('group', flat=True):
            Group.objects.create(facet=facet_key_string, group=add_group)
    elif request.POST.get('delete_facet') == facet_key_string:
        if Facet.objects.filter(number=facet_key_string)[0].displayname != settings.HOMEPAGE_SUBJECTS_DEFAULT_FACET_NAME:
            for group in Group.objects.filter(facet=facet_key_string):
                GroupOfLanguage.objects.filter(group=group).delete()
            Group.objects.filter(facet=facet_key_string).delete()
            Facet.objects.filter(number=facet_key_string).delete()
            FacetOfCourse.objects.filter(facet=facet_key_string).delete()
        return redirect('/home/')

    return render_to_response('facet.html', {
        'context_facet': facet_key_string,
        'displayname': Facet.objects.get(number=facet_key_string).displayname,
        'items': [group for group in Group.objects.filter(facet=facet_key_string)]
    })


@expect_json
def _create_facet(request):
    """
    Helper method for creating a new facet.
    """
    display_name = None
    try:
        display_name = request.json['display_name']
        comment = request.json['comment']
        Facet.objects.create(displayname=display_name, comment=comment)
        number = Facet.objects.get(displayname=display_name).number

    except KeyError as error:
        log.exception("Unable to create facet - missing required JSON key.")
        return JsonResponseBadRequest({
            "ErrMsg": _("Unable to create facet - missing required field '{field}'").format(field=error.message)
        })
    except InvalidKeyError as error:
        log.exception("Unable to create facet - invalid name.")
        return JsonResponseBadRequest({
            "ErrMsg": _("Unable to create facet '{name}'.\n\n{err}").format(name=display_name, err=error.message)
        })
    except IntegrityError:
        log.exception("Unable to create facet - one already exists with the same name.")
        return JsonResponseBadRequest({
            'ErrMsg': _(
                'There is already a facet defined with the same facet name. '
                'Please change your facet name so that it is unique.'
            )
        })

    return JsonResponse({
        'url': reverse_facet_url('facet_handler', number),
    })
