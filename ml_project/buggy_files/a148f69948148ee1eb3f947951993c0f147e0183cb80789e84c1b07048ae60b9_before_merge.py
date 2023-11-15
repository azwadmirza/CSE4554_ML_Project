def setvalue(*args):
    '''
    Set a value for a specific augeas path

    CLI Example:

    .. code-block:: bash

        salt '*' augeas.setvalue /files/etc/hosts/1/canonical localhost

    This will set the first entry in /etc/hosts to localhost

    CLI Example:

    .. code-block:: bash

        salt '*' augeas.setvalue /files/etc/hosts/01/ipaddr 192.168.1.1 \\
                                 /files/etc/hosts/01/canonical test

    Adds a new host to /etc/hosts the ip address 192.168.1.1 and hostname test

    CLI Example:

    .. code-block:: bash

        salt '*' augeas.setvalue prefix=/files/etc/sudoers/ \\
                 "spec[user = '%wheel']/user" "%wheel" \\
                 "spec[user = '%wheel']/host_group/host" 'ALL' \\
                 "spec[user = '%wheel']/host_group/command[1]" 'ALL' \\
                 "spec[user = '%wheel']/host_group/command[1]/tag" 'PASSWD' \\
                 "spec[user = '%wheel']/host_group/command[2]" '/usr/bin/apt-get' \\
                 "spec[user = '%wheel']/host_group/command[2]/tag" NOPASSWD

    Ensures that the following line is present in /etc/sudoers::

        %wheel ALL = PASSWD : ALL , NOPASSWD : /usr/bin/apt-get , /usr/bin/aptitude
    '''
    aug = Augeas()
    ret = {'retval': False}

    tuples = filter(lambda x: not x.startswith('prefix='), args)
    prefix = filter(lambda x: x.startswith('prefix='), args)
    if prefix:
        if len(prefix) > 1:
            raise SaltInvocationError(
                'Only one \'prefix=\' value is permitted'
            )
        else:
            prefix = prefix[0].split('=', 1)[1]

    if len(tuples) % 2 != 0:
        raise SaltInvocationError('Uneven number of path/value arguments')

    tuple_iter = iter(tuples)
    for path, value in zip(tuple_iter, tuple_iter):
        target_path = path
        if prefix:
            target_path = os.path.join(prefix.rstrip('/'), path.lstrip('/'))
        try:
            aug.set(target_path, str(value))
        except ValueError as err:
            ret['error'] = 'Multiple values: {0}'.format(err)

    try:
        aug.save()
        ret['retval'] = True
    except IOError as err:
        ret['error'] = str(err)
    return ret