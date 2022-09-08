# Create your views here.
from rest_framework.response import Response
from rest_framework import (status, viewsets, permissions, authentication)
from django.utils.translation import ugettext as _
from .models import GroupOfLanguage, Group
from .serializers import GroupOfLanguageSerializer
import logging

log = logging.getLogger(__name__)


class IsAdminUserOrTeacherUser(permissions.IsAdminUser):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        try:
            is_teacher = bool(request.user.teacher)
        except Exception:
            is_teacher = False
        return request.user and (request.user.is_staff or is_teacher)


class GroupViewSet(viewsets.ViewSet):
    """
        **Use Cases**

            Post, delete are supported.

        **Example Requests**

            POST /api/v1/group/[facet_id]
            Delete /api/v1/group/[facet_id]

       """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (IsAdminUserOrTeacherUser,)

    def create(self, request):
        serializer = GroupOfLanguageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def remove(self, request):
        lang = request.data.get('lang')
        group_id = request.data.get('group')
        if lang and group_id:
            GroupOfLanguage.objects.filter(lang=lang, group_id=group_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            errors = {}
            if not lang:
                errors["lang"]= [_('This field is required.')]
            if not group_id:
                errors["group"] = [_('This field is required.')]
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
