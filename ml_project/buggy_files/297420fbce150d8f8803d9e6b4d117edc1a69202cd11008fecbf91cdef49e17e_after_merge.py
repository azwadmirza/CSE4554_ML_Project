def mount(location, access='rw'):
    '''
    Mount an image

    CLI Example:

    .. code-block:: bash

        salt '*' guest.mount /srv/images/fedora.qcow
    '''
    root = os.path.join(
            tempfile.gettempdir(),
            'guest',
            location.lstrip(os.sep).replace('/', '.')
            )
    if not os.path.isdir(root):
        try:
            os.makedirs(root)
        except OSError:
            # somehow the directory already exists
            pass
    while True:
        if os.listdir(root):
            # Stuf is in there, don't use it
            hash_type = getattr(hashlib, __opts__.get('hash_type', 'md5'))
            rand = hash_type(str(random.randint(1, 1000000))).hexdigest()
            root = os.path.join(
                tempfile.gettempdir(),
                'guest',
                location.lstrip(os.sep).replace('/', '.') + rand
                )
        else:
            break
    cmd = 'guestmount -i -a {0} --{1} {2}'.format(location, access, root)
    __salt__['cmd.run'](cmd)
    return root