def sealedbox_encrypt(data, **kwargs):
    '''
    Encrypt data using a public key generated from `nacl.keygen`.
    The encryptd data can be decrypted using `nacl.sealedbox_decrypt` only with the secret key.

    CLI Examples:

    .. code-block:: bash

        salt-run nacl.sealedbox_encrypt datatoenc
        salt-call --local nacl.sealedbox_encrypt datatoenc pk_file=/etc/salt/pki/master/nacl.pub
        salt-call --local nacl.sealedbox_encrypt datatoenc pk='vrwQF7cNiNAVQVAiS3bvcbJUnF0cN6fU9YTZD9mBfzQ='
    '''
    pk = _get_pk(**kwargs)
    b = libnacl.sealed.SealedBox(pk)
    return base64.b64encode(b.encrypt(data))