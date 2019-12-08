import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:
    """
    Simple AES cipher used to provide cookie support to the frontend.
    """

    def __init__(self, key: str) -> None:
        self.__padamt = 16
        self.__key = hashlib.sha256(key.encode('utf-8')).digest()

    def __pad(self, s: str) -> str:
        intermediate = "{}.{}".format(len(s), s)
        while len(intermediate) % self.__padamt != 0:
            intermediate = intermediate + '-'
        return intermediate

    def __unpad(self, s: str) -> str:
        length, string = s.split('.', 1)
        intlength = int(length)
        return string[:intlength]

    def encrypt(self, raw: str) -> str:
        raw = self.__pad(raw)
        random = Random.new()  # type: ignore
        iv = random.read(AES.block_size)
        cipher = AES.new(self.__key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8')), altchars=b"._").decode('utf-8')

    def decrypt(self, encoded: str) -> str:
        enc = base64.b64decode(encoded.encode('utf-8'), altchars=b"._")
        iv = enc[:AES.block_size]
        cipher = AES.new(self.__key, AES.MODE_CBC, iv)
        return self.__unpad(cipher.decrypt(enc[AES.block_size:]).decode('utf-8'))
