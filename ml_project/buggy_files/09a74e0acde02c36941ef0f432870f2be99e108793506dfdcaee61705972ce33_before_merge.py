def import_key(text=None, filename=None, user=None, gnupghome=None):
    r"""
    Import a key from text or file

    text
        The text containing to import.

    filename
        The filename containing the key to import.

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    gnupghome
        Specify the location where GPG keyring and related files are stored.

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.import_key text='-----BEGIN PGP PUBLIC KEY BLOCK-----\n ... -----END PGP PUBLIC KEY BLOCK-----'
        salt '*' gpg.import_key filename='/path/to/public-key-file'

    """
    ret = {"res": True, "message": ""}

    gpg = _create_gpg(user, gnupghome)

    if not text and not filename:
        raise SaltInvocationError("filename or text must be passed.")

    if filename:
        try:
            with salt.utils.files.flopen(filename, "rb") as _fp:
                text = salt.utils.stringutils.to_unicode(_fp.read())
        except IOError:
            raise SaltInvocationError("filename does not exist.")

    imported_data = gpg.import_keys(text)

    if GPG_1_3_1:
        counts = imported_data.counts
        if counts.get("imported") or counts.get("imported_rsa"):
            ret["message"] = "Successfully imported key(s)."
        elif counts.get("unchanged"):
            ret["message"] = "Key(s) already exist in keychain."
        elif counts.get("not_imported"):
            ret["res"] = False
            ret["message"] = "Unable to import key."
        elif not counts.get("count"):
            ret["res"] = False
            ret["message"] = "Unable to import key."
    else:
        if imported_data.imported or imported_data.imported_rsa:
            ret["message"] = "Successfully imported key(s)."
        elif imported_data.unchanged:
            ret["message"] = "Key(s) already exist in keychain."
        elif imported_data.not_imported:
            ret["res"] = False
            ret["message"] = "Unable to import key."
        elif not imported_data.count:
            ret["res"] = False
            ret["message"] = "Unable to import key."
    return ret