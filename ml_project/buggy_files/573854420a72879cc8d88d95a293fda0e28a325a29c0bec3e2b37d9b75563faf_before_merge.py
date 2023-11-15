def present(
        name,
        user,
        enc='ssh-rsa',
        comment='',
        source='',
        options=None,
        config='.ssh/authorized_keys',
        **kwargs):
    '''
    Verifies that the specified SSH key is present for the specified user

    name
        The SSH key to manage

    user
        The user who owns the SSH authorized keys file to modify

    enc
        Defines what type of key is being used; can be ed25519, ecdsa, ssh-rsa
        or ssh-dss

    comment
        The comment to be placed with the SSH public key

    source
        The source file for the key(s). Can contain any number of public keys,
        in standard "authorized_keys" format. If this is set, comment and enc
        will be ignored.

    .. note::
        The source file must contain keys in the format ``<enc> <key>
        <comment>``. If you have generated a keypair using PuTTYgen, then you
        will need to do the following to retrieve an OpenSSH-compatible public
        key.

        1. In PuTTYgen, click ``Load``, and select the *private* key file (not
           the public key), and click ``Open``.
        2. Copy the public key from the box labeled ``Public key for pasting
           into OpenSSH authorized_keys file``.
        3. Paste it into a new file.

    options
        The options passed to the key, pass a list object

    config
        The location of the authorized keys file relative to the user's home
        directory, defaults to ".ssh/authorized_keys". Token expansion %u and
        %h for username and home path supported.
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}

    if source == '':
        # check if this is of form {options} {enc} {key} {comment}
        sshre = re.compile(r'^(.*?)\s?((?:ssh\-|ecds)[\w-]+\s.+)$')
        fullkey = sshre.search(name)
        # if it is {key} [comment]
        if not fullkey:
            key_and_comment = name.split(None, 1)
            name = key_and_comment[0]
            if len(key_and_comment) == 2:
                comment = key_and_comment[1]
        else:
            # if there are options, set them
            if fullkey.group(1):
                options = fullkey.group(1).split(',')
            # key is of format: {enc} {key} [comment]
            comps = fullkey.group(2).split(None, 2)
            enc = comps[0]
            name = comps[1]
            if len(comps) == 3:
                comment = comps[2]

    if __opts__['test']:
        ret['result'], ret['comment'] = _present_test(
                user,
                name,
                enc,
                comment,
                options or [],
                source,
                config,
                )
        return ret

    if source != '':
        key = __salt__['cp.get_file_str'](
                source,
                saltenv=__env__)
        filehasoptions = False
        # check if this is of form {options} {enc} {key} {comment}
        sshre = re.compile(r'^(ssh\-|ecds).*')
        key = key.rstrip().split('\n')
        for keyline in key:
            filehasoptions = sshre.match(keyline)
            if not filehasoptions:
                data = __salt__['ssh.set_auth_key_from_file'](
                        user,
                        source,
                        config,
                        saltenv=__env__)
            else:
                # Split keyline to get key und commen
                keyline = keyline.split(' ')
                key_type = keyline[0]
                key_value = keyline[1]
                key_comment = keyline[2] if len(keyline) > 2 else ''
                data = __salt__['ssh.set_auth_key'](
                        user,
                        key_value,
                        key_type,
                        key_comment,
                        options or [],
                        config)
    else:
        data = __salt__['ssh.set_auth_key'](
                user,
                name,
                enc,
                comment,
                options or [],
                config)

    if data == 'replace':
        ret['changes'][name] = 'Updated'
        ret['comment'] = ('The authorized host key {0} for user {1} was '
                          'updated'.format(name, user))
        return ret
    elif data == 'no change':
        ret['comment'] = ('The authorized host key {0} is already present '
                          'for user {1}'.format(name, user))
    elif data == 'new':
        ret['changes'][name] = 'New'
        ret['comment'] = ('The authorized host key {0} for user {1} was added'
                          .format(name, user))
    elif data == 'fail':
        ret['result'] = False
        err = sys.modules[
            __salt__['test.ping'].__module__
        ].__context__.pop('ssh_auth.error', None)
        if err:
            ret['comment'] = err
        else:
            ret['comment'] = ('Failed to add the ssh key. Is the home '
                              'directory available, and/or does the key file '
                              'exist?')
    elif data == 'invalid':
        ret['result'] = False
        ret['comment'] = 'Invalid public ssh key, most likely has spaces'

    return ret