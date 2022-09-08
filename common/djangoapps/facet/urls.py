from django.conf.urls import include, url

from .views import GroupViewSet
GROUP = GroupViewSet.as_view({
    'post': 'create',
    'delete': 'remove'
})

urlpatterns = [
    url(r'^api/v1/group', GROUP),
]
