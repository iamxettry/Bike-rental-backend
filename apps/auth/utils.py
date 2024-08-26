from django.contrib.auth.hashers import BasePasswordHasher
from rest_framework import exceptions
from django.utils.translation import gettext as _

from django.utils.crypto import get_random_string
import hashlib
import random
import re

class CustomSHA512PasswordHasher(BasePasswordHasher):
    """
    A custom password hasher that uses SHA-512.
    """
    algorithm = "custom_sha512"

    def salt(self):
        return get_random_string(16)

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        hash = hashlib.sha512((salt + password).encode('utf-8')).hexdigest()
        truncated_hash = hash[:128]
        encoded = "%s$%s$%s" % (self.algorithm, salt, truncated_hash)
        return encoded

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        encoded_2 = self.encode(password, salt)
        return encoded == encoded_2


    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        encoded_2 = self.encode(password, salt)
        return encoded == encoded_2

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        pass



def generate_random_digit(range):

    return random.randint(1,range);

# Generate username
def generate_userName(first_name, last_name):
    length = generate_random_digit(3)
    digit = get_random_string(length,allowed_chars="0123456789")
    username=first_name+last_name+digit
    return username


class CustomPasswordValidator:
    def __call__(self, password):

        if len(password) < 8 or len(password) > 24:
            raise exceptions.APIException(_("Password must be between 8 and 24 characters long."))
        if not re.search(r'[a-z]', password):
            raise exceptions.APIException(_("Password must contain at least one lowercase letter."))
        if not re.search(r'[A-Z]', password):
            raise exceptions.APIException(_("Password must contain at least one uppercase letter."))
        if not re.search(r'[0-9]', password):
            raise exceptions.APIException(_("Password must contain at least one number."))
        if not re.search(r'[!@#$%]', password):
            raise exceptions.APIException(_("Password must contain at least one special character (!@#$%)."))


    def get_help_text(self):
        return _(
            "Your password must be between 8 and 24 characters long, contain at least one lowercase letter, "
            "one uppercase letter, one number, and one special character (!@#$%)."
        )