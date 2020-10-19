from partage_pedago import ConfigParser, ParsingError, Crypto
import re


class SafeConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        key = kwargs.pop('crypt_key', None)
        if key is not None:
            self.crypto = Crypto(key)
        else:
            self.crypto = Crypto()

        self.crypt_key = self.crypto.gen_key()
        ConfigParser.__init__(self, *args, **kwargs)

    def get(self, section, option, *args, **kwargs):
        raw_val = ConfigParser.get(self, section, option, *args, **kwargs)
        get_raw = kwargs.pop('raw', None)
        if get_raw:
            return raw_val
        return self.process_key(raw_val)

    def set(self, section, option, value=None, encrypted=False):
        if not encrypted:
            super().set(section, option, value)
        else:
            value = self._encrypt(value)
            super().set(section, option, value)

    def process_key(self, raw_val):
        val = raw_val
        encoded_val = re.search(r"ENC\[(.*)]", raw_val, re.IGNORECASE)
        if encoded_val and self.crypt_key:
            val = self._decrypt(raw_val)
        return val

    def __getitem__(self, key):
        print("__getitem__")
        raw_val = super().__getitem__(key)
        return self.process_key(raw_val)

    def _encrypt(self, msg):
        crypto = Crypto(self.crypt_key)
        return crypto.encrypt(msg)

    def _decrypt(self, msg):
        crypto = Crypto(self.crypt_key)
        return crypto.decrypt(msg)
