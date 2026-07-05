from secrets import choice
from string import ascii_letters, digits, punctuation

class PasswordGenerator:
    def __init__(self, length: int):
        self.length = length
        self.password = self._generate_password()

    def _generate_password(self) -> str:
        alphabet = ascii_letters + digits + punctuation
        return ''.join(choice(alphabet) for i in range(self.length))