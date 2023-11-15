def private_key_managed(name,
                        bits=2048,
                        passphrase=None,
                        cipher='aes_128_cbc',
                        new=False,
                        overwrite=False,
                        verbose=True,
                        **kwargs):
    '''
    Manage a private key's existence.

    name:
        Path to the private key

    bits:
        Key length in bits. Default 2048.

    passphrase:
        Passphrase for encrypting the private key.

    cipher:
        Cipher for encrypting the private key.

    new:
        Always create a new key. Defaults to False.
        Combining new with :mod:`prereq <salt.states.requsities.preqreq>`, or when used as part of a `managed_private_key` can allow key rotation whenever a new certificiate is generated.

    overwrite:
        Overwrite an existing private key if the provided passphrase cannot decrypt it.

    verbose:
        Provide visual feedback on stdout, dots while key is generated.
        Default is True.

        .. versionadded:: 2016.11.0

    kwargs:
        Any kwargs supported by file.managed are supported.

    Example:

    The jinja templating in this example ensures a private key is generated if the file doesn't exist
    and that a new private key is generated whenever the certificate that uses it is to be renewed.

    .. code-block:: yaml

        /etc/pki/www.key:
          x509.private_key_managed:
            - bits: 4096
            - new: True
            {% if salt['file.file_exists']('/etc/pki/ca.key') -%}
            - prereq:
              - x509: /etc/pki/www.crt
            {%- endif %}
    '''
    file_args, kwargs = _get_file_args(name, **kwargs)
    new_key = False
    if _check_private_key(
            name, bits=bits, passphrase=passphrase, new=new, overwrite=overwrite):
        file_args['contents'] = __salt__['x509.get_pem_entry'](
            name, pem_type='RSA PRIVATE KEY')
    else:
        new_key = True
        file_args['contents'] = __salt__['x509.create_private_key'](
            text=True, bits=bits, passphrase=passphrase, cipher=cipher, verbose=verbose)

    # Ensure the key contents are a string before passing it along
    file_args['contents'] = salt.utils.stringutils.to_str(file_args['contents'])

    ret = __states__['file.managed'](**file_args)
    if ret['changes'] and new_key:
        ret['changes'] = {'new': 'New private key generated'}

    return ret