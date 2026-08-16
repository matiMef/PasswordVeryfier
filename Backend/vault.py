from base64 import b64encode
from json import dumps, loads
from secrets import token_bytes
from hashlib import pbkdf2_hmac
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


class AuthService:
    def __init__(self):
        self.current_file = Path(__file__).resolve()
        self.current_dir = self.current_file.parent
        self.filepath = self.current_dir.parent / "Interface"

    def verify_password(self, plain_password: str) -> bool:
        if not plain_password:
            return False

        handler = VaultHandler("vault.json", self.filepath, plain_password)

        try:
            return handler.check_password()
        except (FileNotFoundError, ValueError, OSError):
            return False


class JsonPassword:
    def __init__(self, id: int, name: str, password: str):
        self.id = id
        self.name = name
        self.password = password

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password,
        }


class StoredPasswords:
    def __init__(self):
        self.passwords = []

    def get_passwords(self) -> list:
        return self.passwords

    def get_password(self, id) -> list:
        return [p.password for p in self.passwords if id == p.id]

    def set_passwords(self, passwords: list) -> None:
        self.passwords = passwords

    def add_password(self, name: str, password: str) -> None:
        new_id = max([p.id for p in self.passwords], default=0) + 1
        new_password_obj = JsonPassword(new_id, name, password)
        self.passwords.append(new_password_obj)

    def delete_password(self, id: int) -> None:
        self.passwords = [p for p in self.passwords if p.id != id]


class VaultHandler:
    def __init__(self, name: str, raw_path, password: str | None = None):
        self.filename = name
        self.filepath = Path(raw_path) / name
        self.master_password = password

    def check_file(self) -> bool:
        return self.filepath.exists()

    def create_file(self) -> None:
        if self.check_file():
            return

        self.encrypt_file([])

    def _decrypt_file(self) -> list:
        if not self.master_password:
            raise ValueError("Password cannot be empty")

        if not self.check_file():
            raise FileNotFoundError("Vault file not found")

        with open(self.filepath, "rb") as file:
            file_content = file.read()

        if len(file_content) < 16:
            raise ValueError("Vault file is corrupted")

        salt = file_content[:16]
        encrypted_file = file_content[16:]

        if not encrypted_file:
            raise ValueError("Vault file is empty")

        password_bytes = self.master_password.encode("utf-8")
        key = pbkdf2_hmac("sha256", password_bytes, salt, 647149)
        f = Fernet(b64encode(key))

        try:
            decrypted_file = f.decrypt(encrypted_file)
            data = loads(decrypted_file.decode("utf-8"))
            return data if isinstance(data, list) else []
        except (InvalidToken, ValueError, TypeError):
            raise ValueError("Wrong master password")

    def check_password(self) -> bool:
        if not self.master_password:
            return False

        try:
            self._decrypt_file()
            return True
        except (FileNotFoundError, ValueError, InvalidToken, IndexError, OSError):
            return False

    def decrypt_and_load(self) -> list:
        try:
            if not self.master_password:
                raise ValueError("Password cannot be empty")
            
            loaded_passwords = []
            raw_data = self._decrypt_file()

            for item in raw_data:
                obj = JsonPassword(item["id"], item["name"], item["password"])
                loaded_passwords.append(obj)
            return loaded_passwords
        except Exception as e:
            raise ValueError(f"{e}")

    def encrypt_file(self, password_objects: list) -> None:
        try:
            if not self.master_password:
                raise ValueError("Password cannot be empty")
            
            password = self.master_password

            salt = token_bytes(16)
            password_bytes = password.encode("utf-8")

            key = pbkdf2_hmac("sha256", password_bytes, salt, 647149)
            f = Fernet(b64encode(key))

            serializable_data = [p.to_dict() for p in password_objects]
            encoded_file = dumps(serializable_data)
            token = f.encrypt(encoded_file.encode("utf-8"))

            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "wb") as file:
                file.write(salt)
                file.write(token)
        except Exception as e:
            raise ValueError(f"{e}")