def install_file(package, formula_tar, member, formula_def, conn=None):
    '''
    Install a single file to the file system
    '''
    if member.name == package:
        return False

    if conn is None:
        conn = init()

    node_type = six.text_type(__opts__.get('spm_node_type'))

    out_path = conn['formula_path']

    tld = formula_def.get('top_level_dir', package)
    new_name = member.name.replace('{0}/'.format(package), '', 1)
    if not new_name.startswith(tld) and not new_name.startswith('_') and not \
            new_name.startswith('pillar.example') and not new_name.startswith('README'):
        log.debug('%s not in top level directory, not installing', new_name)
        return False

    for line in formula_def.get('files', []):
        tag = ''
        for ftype in FILE_TYPES:
            if line.startswith('{0}|'.format(ftype)):
                tag = line.split('|', 1)[0]
                line = line.split('|', 1)[1]
        if tag and new_name == line:
            if tag in ('c', 'd', 'g', 'l', 'r'):
                out_path = __opts__['spm_share_dir']
            elif tag in ('s', 'm'):
                pass

    if member.name.startswith('{0}/_'.format(package)):
        if node_type in ('master', 'minion'):
            # Module files are distributed via extmods directory
            member.name = new_name.name.replace('{0}/_'.format(package), '')
            out_path = os.path.join(
                salt.syspaths.CACHE_DIR,
                node_type,
                'extmods',
            )
        else:
            # Module files are distributed via _modules, _states, etc
            member.name = new_name.name.replace('{0}/'.format(package), '')
    elif member.name == '{0}/pillar.example'.format(package):
        # Pillars are automatically put in the pillar_path
        member.name = '{0}.sls.orig'.format(package)
        out_path = conn['pillar_path']
    elif package.endswith('-conf'):
        # Configuration files go into /etc/salt/
        member.name = member.name.replace('{0}/'.format(package), '')
        out_path = salt.syspaths.CONFIG_DIR
    elif package.endswith('-reactor'):
        # Reactor files go into /srv/reactor/
        out_path = __opts__['reactor_path']

    # This ensures that double directories (i.e., apache/apache/) don't
    # get created
    comps = member.path.split('/')
    if len(comps) > 1 and comps[0] == comps[1]:
        member.path = '/'.join(comps[1:])

    log.debug('Installing package file %s to %s', member.name, out_path)
    formula_tar.extract(member, out_path)

    return out_path