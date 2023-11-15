def load_privatekey(path, passphrase=None, check_passphrase=True, content=None, backend='pyopenssl'):
    """Load the specified OpenSSL private key.

    The content can also be specified via content; in that case,
    this function will not load the key from disk.
    """

    try:
        if content is None:
            with open(path, 'rb') as b_priv_key_fh:
                priv_key_detail = b_priv_key_fh.read()
        else:
            priv_key_detail = content

        if backend == 'pyopenssl':

            # First try: try to load with real passphrase (resp. empty string)
            # Will work if this is the correct passphrase, or the key is not
            # password-protected.
            try:
                result = crypto.load_privatekey(crypto.FILETYPE_PEM,
                                                priv_key_detail,
                                                to_bytes(passphrase or ''))
            except crypto.Error as e:
                if len(e.args) > 0 and len(e.args[0]) > 0:
                    if e.args[0][0][2] in ('bad decrypt', 'bad password read'):
                        # This happens in case we have the wrong passphrase.
                        if passphrase is not None:
                            raise OpenSSLBadPassphraseError('Wrong passphrase provided for private key!')
                        else:
                            raise OpenSSLBadPassphraseError('No passphrase provided, but private key is password-protected!')
                raise OpenSSLObjectError('Error while deserializing key: {0}'.format(e))
            if check_passphrase:
                # Next we want to make sure that the key is actually protected by
                # a passphrase (in case we did try the empty string before, make
                # sure that the key is not protected by the empty string)
                try:
                    crypto.load_privatekey(crypto.FILETYPE_PEM,
                                           priv_key_detail,
                                           to_bytes('y' if passphrase == 'x' else 'x'))
                    if passphrase is not None:
                        # Since we can load the key without an exception, the
                        # key isn't password-protected
                        raise OpenSSLBadPassphraseError('Passphrase provided, but private key is not password-protected!')
                except crypto.Error as e:
                    if passphrase is None and len(e.args) > 0 and len(e.args[0]) > 0:
                        if e.args[0][0][2] in ('bad decrypt', 'bad password read'):
                            # The key is obviously protected by the empty string.
                            # Don't do this at home (if it's possible at all)...
                            raise OpenSSLBadPassphraseError('No passphrase provided, but private key is password-protected!')
        elif backend == 'cryptography':
            try:
                result = load_pem_private_key(priv_key_detail,
                                              passphrase,
                                              cryptography_backend())
            except TypeError as dummy:
                raise OpenSSLBadPassphraseError('Wrong or empty passphrase provided for private key')
            except ValueError as dummy:
                raise OpenSSLBadPassphraseError('Wrong passphrase provided for private key')

        return result
    except (IOError, OSError) as exc:
        raise OpenSSLObjectError(exc)