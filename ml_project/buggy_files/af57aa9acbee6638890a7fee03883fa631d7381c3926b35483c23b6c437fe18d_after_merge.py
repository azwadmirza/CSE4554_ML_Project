def secretbox_decrypt(data, **kwargs):
    '''
    Decrypt data that was encrypted using `nacl.secretbox_encrypt` using the secret key
    that was generated from `nacl.keygen`.

    CLI Examples:

    .. code-block:: bash

        salt-call nacl.secretbox_decrypt pEXHQM6cuaF7A=
        salt-call --local nacl.secretbox_decrypt data='pEXHQM6cuaF7A=' sk_file=/etc/salt/pki/master/nacl
        salt-call --local nacl.secretbox_decrypt data='pEXHQM6cuaF7A=' sk='YmFkcGFzcwo='
    '''
    if data is None:
        return None

    # ensure data is in bytes
    data = salt.utils.stringutils.to_bytes(data)

    key = _get_sk(**kwargs)
    b = libnacl.secret.SecretBox(key=key)
    return b.decrypt(base64.b64decode(data))