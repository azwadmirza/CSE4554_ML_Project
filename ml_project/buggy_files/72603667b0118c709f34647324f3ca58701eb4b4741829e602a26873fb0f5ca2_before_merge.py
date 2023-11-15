def verify(
    text=None, user=None, filename=None, gnupghome=None, signature=None, trustmodel=None
):
    """
    Verify a message or file

    text
        The text to verify.

    filename
        The filename to verify.

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    gnupghome
        Specify the location where GPG keyring and related files are stored.

    signature
        Specify the filename of a detached signature.

        .. versionadded:: 2018.3.0

    trustmodel
        Explicitly define the used trust model. One of:
          - pgp
          - classic
          - tofu
          - tofu+pgp
          - direct
          - always
          - auto

        .. versionadded:: 2019.2.0

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.verify text='Hello there.  How are you?'
        salt '*' gpg.verify filename='/path/to/important.file'
        salt '*' gpg.verify filename='/path/to/important.file' use_passphrase=True
        salt '*' gpg.verify filename='/path/to/important.file' trustmodel=direct

    """
    gpg = _create_gpg(user)
    trustmodels = ("pgp", "classic", "tofu", "tofu+pgp", "direct", "always", "auto")

    if trustmodel and trustmodel not in trustmodels:
        msg = "Invalid trustmodel defined: {}. Use one of: {}".format(
            trustmodel, ", ".join(trustmodels)
        )
        log.warning(msg)
        return {"res": False, "message": msg}

    extra_args = []

    if trustmodel:
        extra_args.extend(["--trust-model", trustmodel])

    if text:
        verified = gpg.verify(text, extra_args=extra_args)
    elif filename:
        if signature:
            # need to call with fopen instead of flopen due to:
            # https://bitbucket.org/vinay.sajip/python-gnupg/issues/76/verify_file-closes-passed-file-handle
            with salt.utils.files.fopen(signature, "rb") as _fp:
                verified = gpg.verify_file(_fp, filename, extra_args=extra_args)
        else:
            with salt.utils.files.flopen(filename, "rb") as _fp:
                verified = gpg.verify_file(_fp, extra_args=extra_args)
    else:
        raise SaltInvocationError("filename or text must be passed.")

    ret = {}
    if verified.trust_level is not None:
        ret["res"] = True
        ret["username"] = verified.username
        ret["key_id"] = verified.key_id
        ret["trust_level"] = VERIFY_TRUST_LEVELS[six.text_type(verified.trust_level)]
        ret["message"] = "The signature is verified."
    else:
        ret["res"] = False
        ret["message"] = "The signature could not be verified."
    return ret