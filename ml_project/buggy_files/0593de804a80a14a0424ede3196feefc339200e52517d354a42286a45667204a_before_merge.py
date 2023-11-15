def get_keychain(journal_name):
    import keyring

    try:
        return keyring.get_password("jrnl", journal_name)
    except RuntimeError:
        return ""