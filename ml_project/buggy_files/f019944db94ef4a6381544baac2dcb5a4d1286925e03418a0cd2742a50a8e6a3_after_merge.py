def create_private_key(path=None,
                       text=False,
                       bits=2048,
                       passphrase=None,
                       cipher='aes_128_cbc',
                       verbose=True):
    '''
    Creates a private key in PEM format.

    path:
        The path to write the file to, either ``path`` or ``text``
        are required.

    text:
        If ``True``, return the PEM text without writing to a file.
        Default ``False``.

    bits:
        Length of the private key in bits. Default 2048

    passphrase:
        Passphrase for encryting the private key

    cipher:
        Cipher for encrypting the private key. Has no effect if passhprase is None.

    verbose:
        Provide visual feedback on stdout. Default True

        .. versionadded:: 2016.11.0

    CLI Example:

    .. code-block:: bash

        salt '*' x509.create_private_key path=/etc/pki/mykey.key
    '''
    if not path and not text:
        raise salt.exceptions.SaltInvocationError(
            'Either path or text must be specified.')
    if path and text:
        raise salt.exceptions.SaltInvocationError(
            'Either path or text must be specified, not both.')

    if verbose:
        _callback_func = M2Crypto.RSA.keygen_callback
    else:
        _callback_func = _keygen_callback

    # pylint: disable=no-member
    rsa = M2Crypto.RSA.gen_key(bits, M2Crypto.m2.RSA_F4, _callback_func)
    # pylint: enable=no-member
    bio = M2Crypto.BIO.MemoryBuffer()
    if passphrase is None:
        cipher = None
    rsa.save_key_bio(
        bio,
        cipher=cipher,
        callback=_passphrase_callback(passphrase))

    if path:
        return write_pem(
            text=bio.read_all(),
            path=path,
            pem_type='(?:RSA )?PRIVATE KEY'
        )
    else:
        return salt.utils.stringutils.to_str(bio.read_all())