def _active_mounts_openbsd(ret):
    '''
    List active mounts on OpenBSD systems
    '''
    for line in __salt__['cmd.run_stdout']('mount -v').split('\n'):
        comps = re.sub(r"\s+", " ", line).split()
        nod = __salt__['cmd.run_stdout']('ls -l {0}'.format(comps[0]))
        nod = ' '.join(nod.split()).split(" ")
        parens = re.findall(r'\((.*?)\)', line, re.DOTALL)
        if len(parens) > 1:
            ret[comps[3]] = {'device': comps[0],
                         'fstype': comps[5],
                         'opts': _resolve_user_group_names(parens[1].split(", ")),
                         'major': str(nod[4].strip(",")),
                         'minor': str(nod[5]),
                         'device_uuid': parens[0]}
        else:
            ret[comps[2]] = {'device': comps[0],
                            'fstype': comps[4],
                            'opts': _resolve_user_group_names(parens[1].split(", "))}
    return ret