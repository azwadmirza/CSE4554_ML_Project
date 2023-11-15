def gen_keys(keydir, keyname, keysize, user=None):
    '''
    Generate a RSA public keypair for use with salt

    :param str keydir: The directory to write the keypair to
    :param str keyname: The type of salt server for whom this key should be written. (i.e. 'master' or 'minion')
    :param int keysize: The number of bits in the key
    :param str user: The user on the system who should own this keypair

    :rtype: str
    :return: Path on the filesystem to the RSA private key
    '''
    base = os.path.join(keydir, keyname)
    priv = '{0}.pem'.format(base)
    pub = '{0}.pub'.format(base)

    gen = RSA.generate(bits=keysize, e=65537)
    if os.path.isfile(priv):
        # Between first checking and the generation another process has made
        # a key! Use the winner's key
        return priv
    cumask = os.umask(191)
    with salt.utils.fopen(priv, 'wb+') as f:
        f.write(gen.exportKey('PEM'))
    os.umask(cumask)
    with salt.utils.fopen(pub, 'wb+') as f:
        f.write(gen.publickey().exportKey('PEM'))
    os.chmod(priv, 256)
    if user:
        try:
            import pwd
            uid = pwd.getpwnam(user).pw_uid
            os.chown(priv, uid, -1)
            os.chown(pub, uid, -1)
        except (KeyError, ImportError, OSError):
            # The specified user was not found, allow the backup systems to
            # report the error
            pass
    return priv