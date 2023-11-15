def delete_key(
    keyid=None,
    fingerprint=None,
    delete_secret=False,
    user=None,
    gnupghome=None,
    use_passphrase=True,
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

    use_passphrase
        Whether to use a passphrase with the signing key. Passphrase is received
        from Pillar.

        .. versionadded: 3003

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

    def __delete_key(fingerprint, secret, use_passphrase):
        if use_passphrase:
            gpg_passphrase = __salt__["pillar.get"]("gpg_passphrase")
            if not gpg_passphrase:
                ret["res"] = False
                ret["message"] = "gpg_passphrase not available in pillar."
                return ret
            else:
                out = gpg.delete_keys(fingerprint, secret, passphrase=gpg_passphrase)
        else:
            out = gpg.delete_keys(fingerprint, secret, expect_passphrase=False)
        return out

    if key:
        fingerprint = key["fingerprint"]
        skey = get_secret_key(keyid, fingerprint, user)
        if skey:
            if not delete_secret:
                ret["res"] = False
                ret[
                    "message"
                ] = "Secret key exists, delete first or pass delete_secret=True."
                return ret
            else:
                if str(__delete_key(fingerprint, True, use_passphrase)) == "ok":
                    # Delete the secret key
                    ret["message"] = "Secret key for {} deleted\n".format(fingerprint)

        # Delete the public key
        if str(__delete_key(fingerprint, False, use_passphrase)) == "ok":
            ret["message"] += "Public key for {} deleted".format(fingerprint)
        ret["res"] = True
        return ret
    else:
        ret["res"] = False
        ret["message"] = "Key not available in keychain."
        return ret