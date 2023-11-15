def delete_key(
    keyid=None, fingerprint=None, delete_secret=False, user=None, gnupghome=None
):
    """
    Get a key from the GPG keychain

    keyid
        The keyid of the key to be deleted.

    fingerprint
        The fingerprint of the key to be deleted.

    delete_secret
        Whether to delete a corresponding secret key prior to deleting the public key.
        Secret keys must be deleted before deleting any corresponding public keys.

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    gnupghome
        Specify the location where GPG keyring and related files are stored.

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.delete_key keyid=3FAD9F1E

        salt '*' gpg.delete_key fingerprint=53C96788253E58416D20BCD352952C84C3252192

        salt '*' gpg.delete_key keyid=3FAD9F1E user=username

        salt '*' gpg.delete_key keyid=3FAD9F1E user=username delete_secret=True

    """
    ret = {"res": True, "message": ""}

    if fingerprint and keyid:
        ret["res"] = False
        ret["message"] = "Only specify one argument, fingerprint or keyid"
        return ret

    if not fingerprint and not keyid:
        ret["res"] = False
        ret["message"] = "Required argument, fingerprint or keyid"
        return ret

    gpg = _create_gpg(user, gnupghome)
    key = get_key(keyid, fingerprint, user)
    if key:
        fingerprint = key["fingerprint"]
        skey = get_secret_key(keyid, fingerprint, user)
        if skey and not delete_secret:
            ret["res"] = False
            ret[
                "message"
            ] = "Secret key exists, delete first or pass delete_secret=True."
            return ret
        elif (
            skey
            and delete_secret
            and six.text_type(gpg.delete_keys(fingerprint, True)) == "ok"
        ):
            # Delete the secret key
            ret["message"] = "Secret key for {0} deleted\n".format(fingerprint)

        # Delete the public key
        if six.text_type(gpg.delete_keys(fingerprint)) == "ok":
            ret["message"] += "Public key for {0} deleted".format(fingerprint)
        ret["res"] = True
        return ret
    else:
        ret["res"] = False
        ret["message"] = "Key not available in keychain."
        return ret