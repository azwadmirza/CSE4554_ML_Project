def get_keychain(journal_name):
    import keyring

    try:
        return keyring.get_password("jrnl", journal_name)
    except keyring.errors.KeyringError as e:
        if not isinstance(e, keyring.errors.NoKeyringError):
            print("Failed to retrieve keyring", file=sys.stderr)
        return ""