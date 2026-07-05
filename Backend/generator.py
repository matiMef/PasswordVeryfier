import string, secrets

class PasswordGenerator:
    def __init__(self, length: int):
        self.length = length
        self.password = self._generate_password()

    def _generate_password(self) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        secure_password = ''.join(secrets.choice(alphabet) for i in range(self.length))
        return secure_password