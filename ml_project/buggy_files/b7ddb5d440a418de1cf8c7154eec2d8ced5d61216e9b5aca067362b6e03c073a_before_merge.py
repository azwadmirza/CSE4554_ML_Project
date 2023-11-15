    def __init__(self):
        super(Wallet, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        # When there is no available keyring backend, we use an unencrypted keyring on Linux since an encrypted keyring
        # requires input from stdin.
        if sys.platform.startswith('linux'):
            from keyrings.alt.file import EncryptedKeyring, PlaintextKeyring
            if isinstance(keyring.get_keyring(), EncryptedKeyring):
                for new_keyring in keyring.backend.get_all_keyring():
                    if isinstance(new_keyring, PlaintextKeyring):
                        keyring.set_keyring(new_keyring)