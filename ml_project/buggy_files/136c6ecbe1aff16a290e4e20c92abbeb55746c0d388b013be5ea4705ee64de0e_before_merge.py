def build_rule(table=None, chain=None, command=None, position='', full=None,
               **kwargs):
    '''
    Build a well-formatted iptables rule based on kwargs. Long options must be
    used (`--jump` instead of `-j`) because they will have the `--` added to
    them. A `table` and `chain` are not required, unless `full` is True.

    If `full` is `True`, then `table`, `chain` and `command` are required.
    `command` may be specified as either a short option ('I') or a long option
    (`--insert`). This will return the iptables command, exactly as it would
    be used from the command line.

    If a position is required (as with `-I` or `-D`), it may be specified as
    `position`. This will only be useful if `full` is True.

    If `connstate` is passed in, it will automatically be changed to `state`.

    CLI Examples:

    .. code-block:: bash

        salt '*' iptables.build_rule match=state connstate=RELATED,ESTABLISHED \\
            jump=ACCEPT
        salt '*' iptables.build_rule filter INPUT command=I position=3 \\
            full=True match=state state=RELATED,ESTABLISHED jump=ACCEPT
    '''
    if 'target' in kwargs:
        kwargs['jump'] = kwargs['target']
        del kwargs['target']

    for ignore in '__id__', 'fun', 'table', 'chain':
        if ignore in kwargs:
            del kwargs[ignore]

    rule = ''

    if 'match' in kwargs:
        rule = '-m {0} '.format(kwargs['match'])
        del kwargs['match']

    if 'state' in kwargs:
        del kwargs['state']

    if 'connstate' in kwargs:
        kwargs['state'] = kwargs['connstate']
        del kwargs['connstate']

    for item in kwargs:
        rule += '--{0} {1} '.format(item, kwargs[item])

    if full is True:
        if not table:
            return 'Error: Table needs to be specified'
        if not chain:
            return 'Error: Chain needs to be specified'
        if not command:
            return 'Error: Command needs to be specified'

        if command in 'ACDIRLSFZNXPE':
            flag = '-'
        else:
            flag = '--'

        return 'iptables {0}{1} {2} {3} {4}'.format(flag, command, chain,
            position, rule)

    return rule