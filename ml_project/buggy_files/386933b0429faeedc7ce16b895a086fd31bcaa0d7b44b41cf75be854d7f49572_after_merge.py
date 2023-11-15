def decrypt(
    user=None,
    text=None,
    filename=None,
    output=None,
    use_passphrase=False,
    gnupghome=None,
    bare=False,
):
    """
    Decrypt a message or file

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    text
        The encrypted text to decrypt.

    filename
        The encrypted filename to decrypt.

    output
        The filename where the decrypted data will be written, default is standard out.

    use_passphrase
        Whether to use a passphrase with the signing key. Passphrase is received
        from Pillar.

    gnupghome
        Specify the location where GPG keyring and related files are stored.

    bare
        If ``True``, return the (armored) decrypted block as a string without the
        standard comment/res dict.

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.decrypt filename='/path/to/important.file.gpg'

        salt '*' gpg.decrypt filename='/path/to/important.file.gpg' use_passphrase=True

    """
    ret = {"res": True, "comment": ""}
    gpg = _create_gpg(user, gnupghome)
    if use_passphrase:
        gpg_passphrase = __salt__["pillar.get"]("gpg_passphrase")
        if not gpg_passphrase:
            raise SaltInvocationError("gpg_passphrase not available in pillar.")
        gpg_passphrase = gpg_passphrase["gpg_passphrase"]
    else:
        gpg_passphrase = None

    if text:
        result = gpg.decrypt(text, passphrase=gpg_passphrase)
    elif filename:
        with salt.utils.files.flopen(filename, "rb") as _fp:
            if output:
                result = gpg.decrypt_file(_fp, passphrase=gpg_passphrase, output=output)
            else:
                result = gpg.decrypt_file(_fp, passphrase=gpg_passphrase)
    else:
        raise SaltInvocationError("filename or text must be passed.")

    if result.ok:
        if not bare:
            if output:
                ret["comment"] = "Decrypted data has been written to {}".format(output)
            else:
                ret["comment"] = result.data
        else:
            ret = result.data
    else:
        if not bare:
            ret["res"] = False
            ret["comment"] = "{}.\nPlease check the salt-minion log.".format(
                result.status
            )
        else:
            ret = False

        log.error(result.stderr)

    return ret