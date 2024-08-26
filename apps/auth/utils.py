from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import get_random_string
import hashlib
import random

class CustomSHA512PasswordHasher(BasePasswordHasher):
    """
    A custom password hasher that uses SHA-512.
    """
    algorithm = "custom_sha512"

    def salt(self):
        print(get_random_string(16));
        return get_random_string(16)

    def encode(self, password, salt):
        assert password is not None
        assert salt is not None
        hash = hashlib.sha512((salt + password).encode('utf-8')).hexdigest()
        return f"{self.algorithm}${salt}${hash}"

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return self.encode(password, salt) == encoded

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        return {
            'algorithm': algorithm,
            'salt': salt,
            'hash': hash[:6] + '...' + hash[-6:],
        }

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