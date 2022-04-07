
__copyright__    = 'Copyright (C) 2022 syamamura'
__version__      = '1.0.0'
__license__      = 'LGPLv2.1'
__author__       = 'gretchi'
__modifier__     = 'gretchi'
__repository__   = 'https://github.com/gretchi/twim'

import os
import hashlib
import base64

from Crypto.Cipher import AES

CONSUMER_KEY = "4aW3Hep5vXrDnfyZ/8Oy2BsYiSmni1V5aw=="
CONSUMER_KEY_NONCE = "tl6wwnn9FMYOJUiWBMAVdg=="
CONSUMER_SECRET = "LnHQL14GYoHOLwwKl7O0rJPJbjF/JZLitJ4nhE15FnNKOPT2o1yWC53Wqt/Rih8DeYE="
CONSUMER_SECRET_NONCE = "YbNfU7S0qWuVEzNR3l16xw=="


class ConsumerKeys(object):
    def __init__(self, app_name, secret, author, author_email, repository_url):
        password = app_name
        password += secret
        password += author
        password += author_email
        password += repository_url
        password += __modifier__
        password += __repository__

        self.key = self._build_key(password)
        self._e_crypto = None

    @property
    def consumer_key(self):
        """復号済みckを取得

        Returns:
            str: ck
        """
        return self._decrypt(CONSUMER_KEY, self._decode_nonce(CONSUMER_KEY_NONCE))

    @property
    def consumer_secret(self):
        """復号済みcsを取得

        Returns:
            str: cs
        """
        return self._decrypt(CONSUMER_SECRET, self._decode_nonce(CONSUMER_SECRET_NONCE))


    def _build_key(self, password):
        """平文からAESブロックサイズの鍵を生成

        Args:
            password (str): パスワード(平文)

        Returns:
            bytes: AESブロックサイズの鍵
        """
        first_hashed = hashlib.sha512(password.encode()).hexdigest().encode()
        key = hashlib.md5(first_hashed).hexdigest().encode()

        return key

    def encrypt(self, data):
        """暗号化

        Args:
            data (bytes): 平文

        Returns:
            str: 暗号文(Base64)
        """
        self._e_crypto = AES.new(self.key, AES.MODE_EAX)

        ciphertext = self._e_crypto.encrypt(data)
        b64_ciphertext = base64.b64encode(ciphertext).decode()

        return b64_ciphertext

    def _decrypt(self, b64_ciphertext, nonce):
        """復号

        Args:
            b64_ciphertext (str): Base64暗号文

        Returns:
            str: 復号テキスト
        """
        crypto = AES.new(self.key, AES.MODE_EAX, nonce=nonce)

        ciphertext = base64.b64decode(b64_ciphertext.encode())
        plaintext = crypto.decrypt(ciphertext).decode()

        return plaintext

    def get_latest_b64_nonce(self):
        """最後の暗号化に使用されたノンス(Base64)を取得

        Returns:
            _type_: _description_
        """
        b64_nonce = base64.b64encode(self._e_crypto.nonce).decode()
        return b64_nonce

    def _decode_nonce(self, b64_nonce):
        """ノンスを取得

        Args:
            b64_nonce (str): Base64 ノンス

        Returns:
            bytes: ノンス
        """
        return base64.b64decode(b64_nonce.encode())
