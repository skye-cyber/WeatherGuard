import base64
import os
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class SecureEncryptor:
    # Default salt (should be changed)
    DEFAULT_SALT = b'\xf3\x02\xb1\x17\xa3\x97\x9d\x18'

    def __init__(self, key: str, salt: bytes = None):
        if not key:
            raise ValueError("Encryption key cannot be empty.")

        self.salt = salt if salt else self.DEFAULT_SALT
        self.key = self.derive_key(key)

    def derive_key(self, key: str) -> bytes:
        """Derive a secure key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100_000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(key.encode()))

    def encrypt(self, text: str) -> str:
        """Encrypt text and return the encoded string."""
        fernet = Fernet(self.key)
        return fernet.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt encrypted text and return the original string."""
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_text.encode()).decode()


def EMD() -> str:
    InitCrypto = SecureEncryptor('weevles2@phantom@weatherGuard')
    RK = InitCrypto.decrypt(
        'gAAAAABnwYLJQ_X-Hn3fB9owGoYiVAF00R0TeHKy4hkI5jxN15p-QNGL0YujNsoFb3ShE4PbeJ21jbQ6mq0QOeC8OgP2nWJjEX4kwk99Rp2wStXAxZAeTSo=')
    return RK


def OPWM() -> str:
    InitCrypto = SecureEncryptor('weevles2@phantom@weatherGuard')
    RK = InitCrypto.decrypt(
        'gAAAAABnwYEz-kXVkkaZX5Uscfh21v9GJH6PKRZ5f1Y1EBF4MYTi8bRwLiFeR1MRo2HayhqHQk3IwbULOHtkbKZNNcq3mUFUTjCDMJ2KGy-zb6TLQf6Vi92oDkdRZtqOV0XL5VVKTV1y')
    return RK


def OPCA() -> str:
    InitCrypto = SecureEncryptor('weevles2@phantom@weatherGuard')
    RK = InitCrypto.decrypt(
        'gAAAAABnwrvj_pTwOgJz-YDcaOO69eR8qNXEThCmmjGMDyxuAnPZlsVV1IAR1pp1_E12v-8fDB6l559QiEvG8Bell0eRCaFO3HOJqUzKK3RO2MZxqL7mzNvZk4aQ34LnNw9j9Ce7LXFX')
    return RK


def LIQA() -> str:
    InitCrypto = SecureEncryptor('weevles2@phantom@weatherGuard')
    RK = InitCrypto.decrypt(
        'gAAAAABnwrxxjz6v71zXtWW-qXzS-9EcRn8z_lwvZ5sz82D6BNo8jyJhymd0CrMWFaIbDwKrT6lEGtxhw661bGwF3okPx-eQTj5tvyWu4yLiUV8yjulXqLwI57YiOOYma4RAXwLmB7H-')
    return RK


# Example Usage:
if __name__ == "__main__":
    '''OPWM()
    user_key = input("Enter encryption key: ")
    encryptor = SecureEncryptor(user_key)

    message = 'pk.e4d47e2a0ef858ff977567a91af035eb'
    encrypted = encryptor.encrypt(message)
    decrypted = encryptor.decrypt(encrypted)

    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")'''
