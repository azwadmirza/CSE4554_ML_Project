def _get_private_key_obj(private_key, passphrase=None):
    '''
    Returns a private key object based on PEM text.
    '''
    private_key = _text_or_file(private_key)
    private_key = get_pem_entry(private_key, pem_type='(?:RSA )?PRIVATE KEY')
    rsaprivkey = M2Crypto.RSA.load_key_string(
        private_key, callback=_passphrase_callback(passphrase))
    evpprivkey = M2Crypto.EVP.PKey()
    evpprivkey.assign_rsa(rsaprivkey)
    return evpprivkey