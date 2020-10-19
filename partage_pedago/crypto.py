import os
import re
from base64 import b64encode, b64decode

from cryptography.hazmat.primitives.ciphers import Cipher, modes, algorithms
from pathlib import Path


class Crypto(object):
    def __init__(self, key: bytes=None):
        self.setup_dirs()
        self.key = None

        if key is None:
            if not self.load_key():
                self.gen_key()
                self.save_key()
        else:
            self.key = key[:32].zfill(32)

    def setup_dirs(self):
        home = str(Path.home())
        work_dir = os.path.join(home, '.partage_pedago')
        keystore = os.path.join(work_dir, 'keystore.dat')
        self.dirs = {
            'home': home,
            'work_dir': work_dir,
            'keystore': keystore
        }

    def encrypt(self, value, associated_data: bytes = b'', stash=None):

        if not value and not isinstance(value, bool):
            return ""

        if stash and 'iv' in stash and 'cleartext' in stash and stash['cleartext'] == value:
            iv = stash['iv']
        else:
            iv = os.urandom(32)

        # Construct an AES-GCM Cipher object with the given key and a
        # randomly generated IV.
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
        ).encryptor()

        # associated_data will be authenticated but not encrypted,
        # it must also be passed in on decryption.
        encryptor.authenticate_additional_data(associated_data)

        # Encrypt the plaintext and get the associated ciphertext.
        # GCM does not require padding.
        ciphertext = encryptor.update(value.encode('utf-8')) + encryptor.finalize()

        if isinstance(value, str):
            valtype = 'str'
        elif isinstance(value, bool):
            valtype = 'bool'
        elif isinstance(value, int):
            valtype = 'int'
        elif isinstance(value, float):
            valtype = 'float'
        else:
            valtype = 'bytes'

        return f"ENC[AES256_GCM,data:{b64encode(ciphertext).decode('utf-8')},iv:{b64encode(iv).decode('utf-8')}," \
               f"tag:{b64encode(encryptor.tag).decode('utf-8')},type:{valtype}]"

    def decrypt(self, value, associated_data: bytes = b'', stash=None):

        val_re = b'^ENC\[AES256_GCM,data:(.+),iv:(.+),tag:(.+),type:(.+)\]'
        res = re.match(val_re, value.encode('utf-8'))

        if res is None:
            return value

        ciphertext = b64decode(res.group(1))
        iv = b64decode(res.group(2))
        tag = b64decode(res.group(3))
        valtype = res.group(4)

        # Construct a Cipher object, with the key, iv, and additionally the
        # GCM tag used for authenticating the message.
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
        ).decryptor()

        # We put associated_data back in or the tag will fail to verify
        # when we finalize the decryptor.
        decryptor.authenticate_additional_data(associated_data)

        # Decryption gets us the authenticated plaintext.
        # If the tag does not match an InvalidTag exception will be raised.
        cleartext = decryptor.update(ciphertext) + decryptor.finalize()

        if stash:
            # save the values for later if we need to reencrypt
            stash['iv'] = iv
            stash['associated_data'] = associated_data
            stash['cleartext'] = cleartext

        if valtype == b'bytes':
            return cleartext
        if valtype == b'str':
            cv = cleartext
            try:
                cv = cleartext.decode('utf-8')
            except UnicodeDecodeError:
                return cleartext
            return cv
        if valtype == b'int':
            return int(cleartext.decode('utf-8'))
        if valtype == b'float':
            return float(cleartext.decode('utf-8'))
        if valtype == b'bool':
            if cleartext.lower() == b'true':
                return True
            return False
        return cleartext


    def gen_key(self):
        if self.key is None:
            self.key = os.urandom(32)
        return self.key

    def load_key(self):
        if (os.path.exists(self.dirs["work_dir"])
                and os.path.exists(self.dirs["keystore"])
                and os.path.isfile(self.dirs["keystore"])):
            f = open(self.dirs["keystore"], "r")
            self.key = bytes.fromhex(''.join(f.readlines()))
            f.close()
            return True
        return False

    def save_key(self):
        if not os.path.exists(self.dirs["work_dir"]):
            os.makedirs(self.dirs["work_dir"])
        f = open(self.dirs["keystore"], "w+")
        f.write(self.key.hex())
        f.close()
