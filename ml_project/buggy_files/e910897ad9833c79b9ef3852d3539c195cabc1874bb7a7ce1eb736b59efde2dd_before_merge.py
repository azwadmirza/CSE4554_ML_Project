def encrypt(
    user=None,
    recipients=None,
    text=None,
    filename=None,
    output=None,
    sign=None,
    use_passphrase=False,
    gnupghome=None,
    bare=False,
):
    """
    Encrypt a message or file

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    recipients
        The fingerprints for those recipient whom the data is being encrypted for.

    text
        The text to encrypt.

    filename
        The filename to encrypt.

    output
        The filename where the signed file will be written, default is standard out.

    sign
        Whether to sign, in addition to encrypt, the data. ``True`` to use
        default key or fingerprint to specify a different key to sign with.

    use_passphrase
        Whether to use a passphrase with the signing key. Passphrase is received
        from Pillar.

    gnupghome
        Specify the location where GPG keyring and related files are stored.

    bare
        If ``True``, return the (armored) encrypted block as a string without
        the standard comment/res dict.

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.encrypt text='Hello there.  How are you?' recipients=recipient@example.com

        salt '*' gpg.encrypt filename='/path/to/important.file' recipients=recipient@example.com

        salt '*' gpg.encrypt filename='/path/to/important.file' use_passphrase=True \\
                             recipients=recipient@example.com

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
        result = gpg.encrypt(text, recipients, passphrase=gpg_passphrase)
    elif filename:
        if GPG_1_3_1:
            # This version does not allow us to encrypt using the
            # file stream # have to read in the contents and encrypt.
            with salt.utils.files.flopen(filename, "rb") as _fp:
                _contents = salt.utils.stringutils.to_unicode(_fp.read())
            result = gpg.encrypt(
                _contents, recipients, passphrase=gpg_passphrase, output=output
            )
        else:
            # This version allows encrypting the file stream
            with salt.utils.files.flopen(filename, "rb") as _fp:
                if output:
                    result = gpg.encrypt_file(
                        _fp,
                        recipients,
                        passphrase=gpg_passphrase,
                        output=output,
                        sign=sign,
                    )
                else:
                    result = gpg.encrypt_file(
                        _fp, recipients, passphrase=gpg_passphrase, sign=sign
                    )
    else:
        raise SaltInvocationError("filename or text must be passed.")

    if result.ok:
        if not bare:
            if output:
                ret["comment"] = "Encrypted data has been written to {0}".format(output)
            else:
                ret["comment"] = result.data
        else:
            ret = result.data
    else:
        if not bare:
            ret["res"] = False
            ret["comment"] = "{0}.\nPlease check the salt-minion log.".format(
                result.status
            )
        else:
            ret = False
        log.error(result.stderr)
    return ret