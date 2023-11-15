def get_keyring():
    """
    Attempts to get secure keyring at runtime if current keyring is insecure.
    Once it finds a secure keyring, it wil always use that keyring
    """
    global _keyring
    if _keyring is None or not _keyring.is_primary:
        if sys.platform == 'darwin':  # Use Keychain on macOS
            from .darwin import VortaDarwinKeyring
            _keyring = VortaDarwinKeyring()
        else:  # Try to use DBus and Gnome-Keyring (available on Linux and *BSD)
            import secretstorage
            from .secretstorage import VortaSecretStorageKeyring

            # secretstorage has two different libraries based on version
            if parse_version(secretstorage.__version__) >= parse_version("3.0.0"):
                from jeepney.wrappers import DBusErrorResponse as DBusException
            else:
                from dbus.exceptions import DBusException

            try:
                _keyring = VortaSecretStorageKeyring()
            except (secretstorage.exceptions.SecretStorageException, DBusException):  # Try to use KWallet (KDE)
                from .kwallet import VortaKWallet5Keyring, KWalletNotAvailableException
                try:
                    _keyring = VortaKWallet5Keyring()
                except KWalletNotAvailableException:  # Save passwords in DB, if all else fails.
                    from .db import VortaDBKeyring
                    _keyring = VortaDBKeyring()
    return _keyring