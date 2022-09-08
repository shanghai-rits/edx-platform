from social_django.models import UserSocialAuth
from django.utils.translation import ugettext as _
from .phone import Phone
import time


class SmsCodeBackend(object):
    @classmethod
    def authenticate(cls, request=None, **kwargs):
        if request is None:
            return None
        phone = kwargs.pop("phone", None)
        sms_code = kwargs.pop("sms_code", None)
        action = kwargs.pop("action")
        conflict = cls.verify_sms_code_and_get_conflict(phone, sms_code, action, request.session)
        if conflict:
            conflict_messages = {
                "sms_code": _(
                    u"Incorrect verification sms code."
                ),
            }
            errors = {
                field: [{"user_message": conflict_messages[field]}]
                for field in conflict
            }
            raise SmsCodeError(user_message=errors)
        return cls.get_user(phone)

    @classmethod
    def verify_sms_code_and_get_conflict(cls, phone, sms_code, action, session):
        sms_conflicts = []
        if sms_code != session.get('sms_code'):
            sms_conflicts.append("sms_code")
        if phone != session.get('phone'):
            sms_conflicts.append("sms_code")
        if session.get('expires', None) is not None:
            if not time.time() < session.get('expires'):
                sms_conflicts.append("sms_code")
        if action != session.get('action'):
            sms_conflicts.append("sms_code")
        return sms_conflicts

    @classmethod
    def get_user(cls, phone):
        user = None
        usa = UserSocialAuth.objects.filter(provider='sms', uid=Phone(phone).make_phone())
        if usa.exists():
            user = usa[0].user
        return user


class SmsCodeError(Exception):
    def __init__(self, user_message, *args, **kwargs):
        self.user_message = user_message
        super(SmsCodeError, self).__init__(self, *args, **kwargs)
