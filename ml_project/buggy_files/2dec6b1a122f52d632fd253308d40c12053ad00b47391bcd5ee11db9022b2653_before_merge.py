def export_key(keyids=None, secret=False, user=None, gnupghome=None):
    """
    Export a key from the GPG keychain

    keyids
        The key ID(s) of the key(s) to be exported. Can be specified as a comma
        separated string or a list. Anything which GnuPG itself accepts to
        identify a key - for example, the key ID or the fingerprint could be
        used.

    secret
        Export the secret key identified by the ``keyids`` information passed.

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as ``salt`` will set the GnuPG home directory to the
        ``/etc/salt/gpgkeys``.

    gnupghome
        Specify the location where GPG keyring and related files are stored.

    CLI Example:

    .. code-block:: bash

        salt '*' gpg.export_key keyids=3FAD9F1E

        salt '*' gpg.export_key keyids=3FAD9F1E secret=True

        salt '*' gpg.export_key keyids="['3FAD9F1E','3FBD8F1E']" user=username

    """
    gpg = _create_gpg(user, gnupghome)

    if isinstance(keyids, six.string_types):
        keyids = keyids.split(",")
    return gpg.export_keys(keyids, secret)