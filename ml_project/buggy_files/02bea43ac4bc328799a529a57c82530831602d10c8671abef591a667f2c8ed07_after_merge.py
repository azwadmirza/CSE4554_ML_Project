def get_public_key(key, passphrase=None, asObj=False):
    '''
    Returns a string containing the public key in PEM format.

    key:
        A path or PEM encoded string containing a CSR, Certificate or
        Private Key from which a public key can be retrieved.

    CLI Example:

    .. code-block:: bash

        salt '*' x509.get_public_key /etc/pki/mycert.cer
    '''

    if isinstance(key, M2Crypto.X509.X509):
        rsa = key.get_pubkey().get_rsa()
        text = b''
    else:
        text = _text_or_file(key)
        text = get_pem_entry(text)

    if text.startswith(b'-----BEGIN PUBLIC KEY-----'):
        if not asObj:
            return text
        bio = M2Crypto.BIO.MemoryBuffer()
        bio.write(text)
        rsa = M2Crypto.RSA.load_pub_key_bio(bio)

    bio = M2Crypto.BIO.MemoryBuffer()
    if text.startswith(b'-----BEGIN CERTIFICATE-----'):
        cert = M2Crypto.X509.load_cert_string(text)
        rsa = cert.get_pubkey().get_rsa()
    if text.startswith(b'-----BEGIN CERTIFICATE REQUEST-----'):
        csr = M2Crypto.X509.load_request_string(text)
        rsa = csr.get_pubkey().get_rsa()
    if (text.startswith(b'-----BEGIN PRIVATE KEY-----') or
            text.startswith(b'-----BEGIN RSA PRIVATE KEY-----')):
        rsa = M2Crypto.RSA.load_key_string(
            text, callback=_passphrase_callback(passphrase))

    if asObj:
        evppubkey = M2Crypto.EVP.PKey()
        evppubkey.assign_rsa(rsa)
        return evppubkey

    rsa.save_pub_key_bio(bio)
    return bio.read_all()