def set_keyring(context, type=""):
    if type == "failed":
        keyring.set_keyring(FailedKeyring())
    else:
        keyring.set_keyring(TestKeyring())