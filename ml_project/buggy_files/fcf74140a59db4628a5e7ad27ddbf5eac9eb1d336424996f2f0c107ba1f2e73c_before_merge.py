def tune(device, **kwargs):
    '''
    Set attributes for the specified device (using tune2fs)

    CLI Example::

        salt '*' extfs.tune /dev/sda1 force=True label=wildstallyns opts='acl,noexec'

    Valid options are::

        max: max mount count
        count: mount count
        error: error behavior
        extended_opts: extended options (comma separated)
        force: force, even if there are errors (set to True)
        group: group name or gid that can use the reserved blocks
        interval: interval between checks
        journal: set to True to create a journal (default on ext3/4)
        journal_opts: options for the fs journal (comma separated)
        label: label to apply to the file system
        reserved: percentage of blocks reserved for super-user
        last_dir: last mounted directory
        opts: mount options (comma separated)
        feature: set or clear a feature (comma separated)
        mmp_check: mmp check interval
        reserved: reserved blocks count
        quota_opts: quota options (comma separated)
        time: time last checked
        user: user or uid who can use the reserved blocks
        uuid: set the UUID for the file system

        see man 8 tune2fs for a more complete description of these options
    '''
    kwarg_map = {'max': 'c',
                 'count': 'C',
                 'error': 'e',
                 'extended_opts': 'E',
                 'force': 'f',
                 'group': 'g',
                 'interval': 'i',
                 'journal': 'j',
                 'journal_opts': 'J',
                 'label': 'L',
                 'last_dir': 'M',
                 'opts': 'o',
                 'feature': 'O',
                 'mmp_check': 'p',
                 'reserved': 'r',
                 'quota_opts': 'Q',
                 'time': 'T',
                 'user': 'u',
                 'uuid': 'U'}
    opts = ''
    for key in kwargs.keys():
        opt = kwarg_map[key]
        if kwargs[key] == 'True':
            opts += '-{0} '.format(opt)
        else:
            opts += '-{0} {1} '.format(opt, kwargs[key])
    cmd = 'tune2fs {0}{1}'.format(opts, device)
    out = __salt__['cmd.run'](cmd).splitlines()
    return out