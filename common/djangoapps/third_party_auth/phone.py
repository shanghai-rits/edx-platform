from django.contrib.auth.hashers import (
    check_password, make_password,
)
import re


class Phone:
    def __init__(self, phone):
        self.phone = phone

    def fuzzy(self, catch=r'^(\d{3})\d*(\d{4})$', replace=r"\1****\2"):
        return re.sub(catch, replace, self.phone)

    def make_phone(self):
        # return make_password(self.phone, salt='20000')
        return self.phone

    def check_phone(self, phone):
        # return check_password(self.phone, phone)
        return phone == self.phone
