from os import path
from base64 import b64encode
from json import loads, dumps
from secrets import token_bytes
from hashlib import pbkdf2_hmac, sha256
from cryptography.fernet import Fernet, InvalidToken

class AuthService:
    def __init__(self):
        # to do
        self.stored_hash="5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"

    def verify_password(self, plain_password: str) -> bool:
        if not plain_password:
            return False
        
        input_hash = sha256(plain_password.encode('utf-8')).hexdigest()
        return input_hash == self.stored_hash

class JsonPassword:
    def __init__(self, id: int, name: str, password: str):
        self.id = id
        self.name = name
        self.password = password

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password
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
    def __init__(self, name: str, raw_path: str, password: str):
        self.filename = name
        self.filepath = path.join(raw_path, name)
        self.master_password = password
        
    def check_file(self) -> bool:
        return path.exists(self.filepath)

    def create_file(self) -> None:
        if self.check_file():
            return

        with open(self.filepath, "wb") as file:
            self.encrypt_file([], self.master_password)

    def _decrypt_file(self) -> list:
        with open(self.filepath, "rb") as file:
            file_content = file.read()
        
        salt = file_content[:16]
        encrypted_file = file_content[16:]
        password_bytes = self.master_password.encode("utf-8") 
        
        key = pbkdf2_hmac('sha256', password_bytes, salt, 647149)
        key = b64encode(key)
        f = Fernet(key)
        
        try:
            decrypted_file = f.decrypt(encrypted_file)
            return loads(decrypted_file.decode("utf-8"))
        
        except InvalidToken:
            raise ValueError("Wrong master password")
        
    def decrypt_and_load(self) -> list:
        loaded_passwords = []
        raw_data = self._decrypt_file()
        
        for item in raw_data:
            obj = JsonPassword(item["id"], item["name"], item["password"])
            loaded_passwords.append(obj)
        return loaded_passwords
        
    def encrypt_file(self, password_objects: list) -> None:
        salt = token_bytes(16)
        password_bytes = self.master_password.encode("utf-8")
        
        key = pbkdf2_hmac('sha256', password_bytes, salt, 647149)
        key = b64encode(key)
        f = Fernet(key)
        
        serializable_data = [p.to_dict() for p in password_objects]
        encoded_file = dumps(serializable_data)
        token = f.encrypt(encoded_file.encode("utf-8"))
        
        with open(self.filepath, "wb") as file:
            file.write(salt)
            file.write(token)