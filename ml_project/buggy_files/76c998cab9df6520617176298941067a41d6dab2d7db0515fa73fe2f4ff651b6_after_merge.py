def receive_keys(keyserver=None, keys=None, user=None, gnupghome=None):
    """
    Receive key(s) from keyserver and add them to keychain

    keyserver
        Keyserver to use for searching for GPG keys, defaults to pgp.mit.edu

    keys
        The keyID(s) to retrieve from the keyserver.  Can be specified as a comma
        separated string or a list.

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    gnupghome
        Specify the location where GPG keyring and related files are stored.

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.receive_keys keys='3FAD9F1E'

        salt '*' gpg.receive_keys keys="['3FAD9F1E','3FBD9F2E']"

        salt '*' gpg.receive_keys keys=3FAD9F1E user=username

    """
    ret = {"res": True, "changes": {}, "message": []}

    gpg = _create_gpg(user, gnupghome)

    if not keyserver:
        keyserver = "pgp.mit.edu"

    if isinstance(keys, str):
        keys = keys.split(",")

    recv_data = gpg.recv_keys(keyserver, *keys)
    for result in recv_data.results:
        if "ok" in result:
            if result["ok"] == "1":
                ret["message"].append(
                    "Key {} added to keychain".format(result["fingerprint"])
                )
            elif result["ok"] == "0":
                ret["message"].append(
                    "Key {} already exists in keychain".format(result["fingerprint"])
                )
        elif "problem" in result:
            ret["message"].append("Unable to add key to keychain")
    return ret