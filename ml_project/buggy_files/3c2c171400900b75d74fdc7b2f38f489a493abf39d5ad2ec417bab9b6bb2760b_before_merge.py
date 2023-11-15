def set_keychain(journal_name, password):
    import keyring

    if password is None:
        try:
            keyring.delete_password("jrnl", journal_name)
        except keyring.errors.PasswordDeleteError:
            pass
    else:
        try:
            keyring.set_password("jrnl", journal_name, password)
        except keyring.errors.NoKeyringError:
            print(
                "Keyring backend not found. Please install one of the supported backends by visiting: https://pypi.org/project/keyring/",
                file=sys.stderr,
            )