def trust_key(keyid=None, fingerprint=None, trust_level=None, user=None):
    """
    Set the trust level for a key in GPG keychain

    keyid
        The keyid of the key to set the trust level for.

    fingerprint
        The fingerprint of the key to set the trust level for.

    trust_level
        The trust level to set for the specified key, must be one
        of the following:
        expired, unknown, not_trusted, marginally, fully, ultimately

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.trust_key keyid='3FAD9F1E' trust_level='marginally'
        salt '*' gpg.trust_key fingerprint='53C96788253E58416D20BCD352952C84C3252192' trust_level='not_trusted'
        salt '*' gpg.trust_key keys=3FAD9F1E trust_level='ultimately' user='username'

    """
    ret = {"res": True, "message": ""}

    _VALID_TRUST_LEVELS = [
        "expired",
        "unknown",
        "not_trusted",
        "marginally",
        "fully",
        "ultimately",
    ]

    if fingerprint and keyid:
        ret["res"] = False
        ret["message"] = "Only specify one argument, fingerprint or keyid"
        return ret

    if not fingerprint:
        if keyid:
            key = get_key(keyid, user=user)
            if key:
                if "fingerprint" not in key:
                    ret["res"] = False
                    ret["message"] = "Fingerprint not found for keyid {0}".format(keyid)
                    return ret
                fingerprint = key["fingerprint"]
            else:
                ret["res"] = False
                ret["message"] = "KeyID {0} not in GPG keychain".format(keyid)
                return ret
        else:
            ret["res"] = False
            ret["message"] = "Required argument, fingerprint or keyid"
            return ret

    if trust_level not in _VALID_TRUST_LEVELS:
        return "ERROR: Valid trust levels - {0}".format(",".join(_VALID_TRUST_LEVELS))

    stdin = "{0}:{1}\n".format(fingerprint, NUM_TRUST_DICT[trust_level])
    cmd = [_gpg(), "--import-ownertrust"]
    _user = user

    if user == "salt":
        homeDir = os.path.join(__salt__["config.get"]("config_dir"), "gpgkeys")
        cmd.extend(["--homedir", homeDir])
        _user = "root"
    res = __salt__["cmd.run_all"](cmd, stdin=stdin, runas=_user, python_shell=False)

    if not res["retcode"] == 0:
        ret["res"] = False
        ret["message"] = res["stderr"]
    else:
        if res["stderr"]:
            _match = re.findall(r"\d", res["stderr"])
            if len(_match) == 2:
                ret["fingerprint"] = fingerprint
                ret["message"] = "Changing ownership trust from {0} to {1}.".format(
                    INV_NUM_TRUST_DICT[_match[0]], INV_NUM_TRUST_DICT[_match[1]]
                )
            else:
                ret["fingerprint"] = fingerprint
                ret["message"] = "Setting ownership trust to {0}.".format(
                    INV_NUM_TRUST_DICT[_match[0]]
                )
        else:
            ret["message"] = res["stderr"]
    return ret