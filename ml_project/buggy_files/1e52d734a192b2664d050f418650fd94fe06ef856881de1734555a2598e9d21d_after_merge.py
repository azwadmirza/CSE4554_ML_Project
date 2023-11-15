def secretbox_encrypt(data, **kwargs):
    '''
    Encrypt data using a secret key generated from `nacl.keygen`.
    The same secret key can be used to decrypt the data using `nacl.secretbox_decrypt`.

    CLI Examples:

    .. code-block:: bash

        salt-run nacl.secretbox_encrypt datatoenc
        salt-call --local nacl.secretbox_encrypt datatoenc sk_file=/etc/salt/pki/master/nacl
        salt-call --local nacl.secretbox_encrypt datatoenc sk='YmFkcGFzcwo='
    '''
    # ensure data is in bytes
    data = salt.utils.stringutils.to_bytes(data)

    sk = _get_sk(**kwargs)
    b = libnacl.secret.SecretBox(sk)
    return base64.b64encode(b.encrypt(data))