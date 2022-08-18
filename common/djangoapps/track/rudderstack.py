"""
Wrapper methods for emitting events to Rudderstack directly (rather than through tracking log events).

These take advantage of properties that are extracted from incoming requests by track middleware,
stored in tracking context objects, and extracted here to be passed to Rudderstack as part of context
required by server-side events.

To use, call "from common.djangoapps.track import rudderstack", then call rudderstack.track() or rudderstack.identify().

"""


import rudder_analytics
from django.conf import settings
from eventtracking import tracker
from six.moves.urllib.parse import urlunsplit

def track(user_id, event_name, properties=None, context=None, traits=None):
    """
    Wrapper for emitting Rudderstack track event, including augmenting context information from middleware.
    """

    if event_name is not None and (hasattr(settings, 'RUDDERSTACK_KEY') and hasattr(settings, 'DATA_PLANE_URL')) and (settings.RUDDERSTACK_KEY and settings.DATA_PLANE_URL):
        properties = properties or {}
        rudderstack_context = dict(context) if context else {}
        tracking_context = tracker.get_tracker().resolve_context()

        if 'ip' not in rudderstack_context and 'ip' in tracking_context:
            rudderstack_context['ip'] = tracking_context.get('ip')

        if ('Google Analytics' not in rudderstack_context or 'clientId' not in rudderstack_context['Google Analytics']) and 'client_id' in tracking_context:  # lint-amnesty, pylint: disable=line-too-long
            rudderstack_context['Google Analytics'] = {
                'clientId': tracking_context.get('client_id')
            }

        if 'userAgent' not in rudderstack_context and 'agent' in tracking_context:
            rudderstack_context['userAgent'] = tracking_context.get('agent')

        path = tracking_context.get('path')
        referer = tracking_context.get('referer')
        page = tracking_context.get('page')

        if path and not page:
            # Try to put together a url from host and path, hardcoding the schema.
            # (Segment doesn't care about the schema for GA, but will extract the host and path from the url.)
            host = tracking_context.get('host')
            if host:
                parts = ("https", host, path, "", "")
                page = urlunsplit(parts)

        if path is not None or referer is not None or page is not None:
            if 'page' not in rudderstack_context:
                rudderstack_context['page'] = {}
            if path is not None and 'path' not in rudderstack_context['page']:
                rudderstack_context['page']['path'] = path
            if referer is not None and 'referrer' not in rudderstack_context['page']:
                rudderstack_context['page']['referrer'] = referer
            if page is not None and 'url' not in rudderstack_context['page']:
                rudderstack_context['page']['url'] = page

        if traits:
            rudderstack_context['traits'] = traits
        
        rudder_analytics.track(user_id, event_name, properties, rudderstack_context)


def identify(user_id, properties, context=None):
    """
    Wrapper for emitting Rudderstack identify event.
    """
    if (hasattr(settings, 'RUDDERSTACK_KEY') and hasattr(settings, 'DATA_PLANE_URL')) and (settings.RUDDERSTACK_KEY and settings.DATA_PLANE_URL):
        rudderstack_context = dict(context) if context else {}
        rudder_analytics.identify(user_id, properties, rudderstack_context)
