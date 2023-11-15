def set_(name, value, **kwargs):
    '''
    Set system rc configuration variables

    CLI Example:

     .. code-block:: bash

         salt '*' sysrc.set name=sshd_flags value="-p 2222"
    '''

    cmd = 'sysrc -v'

    if 'file' in kwargs:
        cmd += ' -f '+kwargs['file']

    if 'jail' in kwargs:
        cmd += ' -j '+kwargs['jail']

    # This is here because the YAML parser likes to convert the string literals
    # YES, NO, Yes, No, True, False, etc. to boolean types.  However, in this case,
    # we will check to see if that happened and replace it with "YES" or "NO" because
    # those items are accepted in sysrc.
    if type(value) == bool:
        if value:
            value = "YES"
        else:
            value = "NO"

    # This is here for the same reason, except for numbers
    if type(value) == int:
        value = str(value)

    cmd += ' '+name+"=\""+value+"\""

    sysrcs = __salt__['cmd.run'](cmd)

    ret = {}
    for sysrc in sysrcs.split("\n"):
        rcfile = sysrc.split(': ')[0]
        var = sysrc.split(': ')[1]
        oldval = sysrc.split(': ')[2].split(" -> ")[0]
        newval = sysrc.split(': ')[2].split(" -> ")[1]
        if rcfile not in ret:
            ret[rcfile] = {}
        ret[rcfile][var] = newval
    return ret