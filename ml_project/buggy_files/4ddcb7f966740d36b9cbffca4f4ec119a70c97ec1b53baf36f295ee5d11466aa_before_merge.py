def sealedbox_decrypt(data, **kwargs):
    '''
    Decrypt data using a secret key that was encrypted using a public key with `nacl.sealedbox_encrypt`.

    CLI Examples:

    .. code-block:: bash

        salt-call nacl.sealedbox_decrypt pEXHQM6cuaF7A=
        salt-call --local nacl.sealedbox_decrypt data='pEXHQM6cuaF7A=' sk_file=/etc/salt/pki/master/nacl
        salt-call --local nacl.sealedbox_decrypt data='pEXHQM6cuaF7A=' sk='YmFkcGFzcwo='
    '''
    if data is None:
        return None
    sk = _get_sk(**kwargs)
    keypair = libnacl.public.SecretKey(sk)
    b = libnacl.sealed.SealedBox(keypair)
    return b.decrypt(base64.b64decode(data))