def keygen(sk_file=None, pk_file=None, **kwargs):
    '''
    Use libnacl to generate a keypair.

    If no `sk_file` is defined return a keypair.

    If only the `sk_file` is defined `pk_file` will use the same name with a postfix `.pub`.

    When the `sk_file` is already existing, but `pk_file` is not. The `pk_file` will be generated
    using the `sk_file`.

    CLI Examples:

    .. code-block:: bash

        salt-run nacl.keygen
        salt-run nacl.keygen sk_file=/etc/salt/pki/master/nacl
        salt-run nacl.keygen sk_file=/etc/salt/pki/master/nacl pk_file=/etc/salt/pki/master/nacl.pub
        salt-run nacl.keygen
    '''

    if 'keyfile' in kwargs:
        salt.utils.versions.warn_until(
            'Fluorine',
            'The \'keyfile\' argument has been deprecated and will be removed in Salt '
            '{version}. Please use \'sk_file\' argument instead.'
        )
        sk_file = kwargs['keyfile']

    if sk_file is None:
        kp = libnacl.public.SecretKey()
        return {'sk': base64.b64encode(kp.sk), 'pk': base64.b64encode(kp.pk)}

    if pk_file is None:
        pk_file = '{0}.pub'.format(sk_file)

    if sk_file and pk_file is None:
        if not os.path.isfile(sk_file):
            kp = libnacl.public.SecretKey()
            with salt.utils.files.fopen(sk_file, 'w') as keyf:
                keyf.write(base64.b64encode(kp.sk))
            if salt.utils.platform.is_windows():
                cur_user = salt.utils.win_functions.get_current_user()
                salt.utils.win_dacl.set_owner(sk_file, cur_user)
                salt.utils.win_dacl.set_permissions(sk_file, cur_user, 'full_control', 'grant', reset_perms=True, protected=True)
            else:
                # chmod 0600 file
                os.chmod(sk_file, 1536)
            return 'saved sk_file: {0}'.format(sk_file)
        else:
            raise Exception('sk_file:{0} already exist.'.format(sk_file))

    if sk_file is None and pk_file:
        raise Exception('sk_file: Must be set inorder to generate a public key.')

    if os.path.isfile(sk_file) and os.path.isfile(pk_file):
        raise Exception('sk_file:{0} and pk_file:{1} already exist.'.format(sk_file, pk_file))

    if os.path.isfile(sk_file) and not os.path.isfile(pk_file):
        # generate pk using the sk
        with salt.utils.files.fopen(sk_file, 'rb') as keyf:
            sk = six.text_type(keyf.read()).rstrip('\n')
            sk = base64.b64decode(sk)
        kp = libnacl.public.SecretKey(sk)
        with salt.utils.files.fopen(pk_file, 'w') as keyf:
            keyf.write(base64.b64encode(kp.pk))
        return 'saved pk_file: {0}'.format(pk_file)

    kp = libnacl.public.SecretKey()
    with salt.utils.files.fopen(sk_file, 'w') as keyf:
        keyf.write(base64.b64encode(kp.sk))
    if salt.utils.platform.is_windows():
        cur_user = salt.utils.win_functions.get_current_user()
        salt.utils.win_dacl.set_owner(sk_file, cur_user)
        salt.utils.win_dacl.set_permissions(sk_file, cur_user, 'full_control', 'grant', reset_perms=True, protected=True)
    else:
        # chmod 0600 file
        os.chmod(sk_file, 1536)
    with salt.utils.files.fopen(pk_file, 'w') as keyf:
        keyf.write(base64.b64encode(kp.pk))
    return 'saved sk_file:{0}  pk_file: {1}'.format(sk_file, pk_file)