from base64 import b64decode, b64encode
from configparser import ConfigParser
from os.path import exists
from time import time
import sys
import ctypes
import getpass

from pythonzimbra.communication import Communication
from pythonzimbra.tools import auth
from pythonzimbra.tools.auth import authenticate

from partage_pedago import Crypto
from partage_pedago.safeconfigparser import SafeConfigParser


class CredsPrompt:
    @staticmethod
    def prompt_mail():
        from email.utils import parseaddr
        mail = ''
        full_name = ''
        valid = False
        while not valid:
            valid = True

            raw = input("Entrez 'Prenom Nom <prenom.nom@site.fr>': ")
            full_name, mail = parseaddr(raw)

            if not mail.endswith("univ-avignon.fr"):
                print("Domaine de mail invalide.")
                valid = False

            if not "@" in mail:
                print("Addresse mail invalide.")
                valid = False

            if not " " in full_name:
                print("Nom invalide.")
                valid = False

            if valid and '"' in full_name:
                full_name.replace('"', '')

        return mail, full_name

    @staticmethod
    def prompt_password():
        p = input('Entrez le mdp: ')
        enc = b64encode(p.encode('utf-8'))
        CredsPrompt.nuke(p)
        return enc.decode()

    @staticmethod
    def nuke(var):
        str_len = len(var)
        offset = sys.getsizeof(var) - str_len - 1
        ctypes.memset(id(var) + offset, 0, str_len)
        del var


class PartageZimbraCom:
    def __init__(self, url: str = 'https://partage.univ-avignon.fr/service/soap'):
        self.url = url
        self.refresh_timestamp()

        self.comm = None
        self.token = None

        self.config = self.get_config()
        self.pre_auth = self.config.get('zimbra', 'password')
        self.mail_addr = self.config.get('zimbra', 'mail')
        self.full_name = self.config.get('zimbra', 'fullName')

    def get_config(self):
        config = SafeConfigParser()

        if not exists('config.ini'):
            mail, full_name = CredsPrompt.prompt_mail()

            # I believe in full-crypto
            config['zimbra'] = {}
            config.set('zimbra', 'mail', mail, encrypted=True)
            config.set('zimbra', 'fullName', full_name, encrypted=True)
            config.set('zimbra', 'password', b64decode(CredsPrompt.prompt_password()).decode("utf-8"), encrypted=True)

            config.write(open('config.ini', 'w+'))
        else:
            config.read('config.ini')

        return config

    def auth(self):
        response = authenticate(
            self.url,
            self.mail_addr,
            self.pre_auth,
            by='name',
            expires=0,
            timestamp=self.timestamp,
            use_password=True,
            raise_on_error=True
        )
        return response

    def get_com(self):
        if self.comm is None:
            self.comm = Communication(self.url)
        return self.comm

    def generate_token(self):
        if self.token is None:
            self.token = auth.authenticate(
                self.url,
                self.mail_addr,
                self.pre_auth,
                by='name',
                expires=0,
                timestamp=self.timestamp,
                use_password=True,
                raise_on_error=True
            )
        return self.token

    def request(self, request):
        response = self.get_com().send_request(request)
        if not response.is_fault():
            print(response.get_response())
        else:
            print(f"error\n"
                  f"fault_message: {response.get_fault_message()}\n"
                  f"fault_code: {response.get_fault_code()}")
        return response

    def gen_base_request(self):
        comm = self.get_com()
        info_request = comm.gen_request(token=self.generate_token())
        return info_request

    @property
    def inbox_request(self):
        req = self.gen_base_request()
        req.add_request(
            'GetFolderRequest',
            {
                'folder': {
                    'path': '/inbox'
                }
            },
            'urn:zimbraMail'
        )
        return req

    def build_msg_request(self, to: dict, subject: str, body: str, html_body: str):
        req = self.gen_base_request()
        req.add_request(
            'SendMsgRequest',
            {
                "m": {
                    "e": [
                        {
                            "t": "t",
                            "a": to['mail'],
                            "p": to['full_name']
                        },
                        {
                            "t": "f",
                            "a": self.mail_addr,
                            "p": self.full_name
                        }
                    ],
                    "su": {
                        "_content": subject
                    },
                    "mp": [
                        {
                            "ct": "multipart/alternative",
                            "mp": [
                                {
                                    "ct": "text/plain",
                                    "content": {
                                        "_content": body
                                    }
                                },
                                {
                                    "ct": "text/html",
                                    "content": {
                                        "_content": f"<html><body><div style=\"font-family: arial, helvetica, "
                                                    f"sans-serif; font-size: 12pt; color: #814503\"><div>"
                                                    f"{html_body}</div></div></body></html> "
                                    }
                                }
                            ]
                        }
                    ]
                }
            },
            'urn:zimbraMail'
        )
        return req

    @property
    def timestamp(self):
        return self._timestampsp

    def refresh_timestamp(self):
        self._timestampsp = int(time() * 1000)


if __name__ == '__main__':
    partage = PartageZimbraCom()

    partage.auth()
    partage.request(partage.inbox_request)
