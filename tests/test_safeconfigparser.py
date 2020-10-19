from unittest import TestCase

from partage_pedago.safeconfigparser import SafeConfigParser


class TestSafeConfigParser(TestCase):
    @classmethod
    def setUp(cls) -> None:
        cls._scp = SafeConfigParser(crypt_key='YoullNeverGuessWhat')
        cls._scp['entry'] = {'name': 'Phoebe'}

    def test_get(self):
        self.assertTrue(self._scp.get('entry', 'name') == 'Phoebe')

    def test_set(self):
        self._scp.set('entry', 'nameEnc', 'Phoebe', True)

        self.assertTrue(self._scp.get('entry', 'nameEnc') == 'Phoebe')