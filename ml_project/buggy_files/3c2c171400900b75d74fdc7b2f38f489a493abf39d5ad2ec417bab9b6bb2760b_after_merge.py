def set_keychain(journal_name, password):
    import keyring

    if password is None:
        try:
            keyring.delete_password("jrnl", journal_name)
        except keyring.errors.KeyringError:
            pass
    else:
        try:
            keyring.set_password("jrnl", journal_name, password)
        except keyring.errors.KeyringError as e:
            if isinstance(e, keyring.errors.NoKeyringError):
                print(
                    "Keyring backend not found. Please install one of the supported backends by visiting: https://pypi.org/project/keyring/",
                    file=sys.stderr,
                )
            else:
                print("Failed to retrieve keyring", file=sys.stderr)