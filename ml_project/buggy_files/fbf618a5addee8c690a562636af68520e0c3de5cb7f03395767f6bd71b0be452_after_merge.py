def build_rule(table='filter', chain=None, command=None, position='', full=None, family='ipv4',
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

        salt '*' iptables.build_rule match=state \\
            connstate=RELATED,ESTABLISHED jump=ACCEPT

        salt '*' iptables.build_rule filter INPUT command=I position=3 \\
            full=True match=state state=RELATED,ESTABLISHED jump=ACCEPT

        salt '*' iptables.build_rule filter INPUT command=A \\
            full=True match=state state=RELATED,ESTABLISHED \\
            source='127.0.0.1' jump=ACCEPT

        .. Invert Rules
        salt '*' iptables.build_rule filter INPUT command=A \\
            full=True match=state state=RELATED,ESTABLISHED \\
            source='! 127.0.0.1' jump=ACCEPT

        salt '*' iptables.build_rule filter INPUT command=A \\
            full=True match=state state=RELATED,ESTABLISHED \\
            destination='not 127.0.0.1' jump=ACCEPT

        IPv6:
        salt '*' iptables.build_rule match=state \\
            connstate=RELATED,ESTABLISHED jump=ACCEPT \\
            family=ipv6
        salt '*' iptables.build_rule filter INPUT command=I position=3 \\
            full=True match=state state=RELATED,ESTABLISHED jump=ACCEPT \\
            family=ipv6

    '''
    if 'target' in kwargs:
        kwargs['jump'] = kwargs.pop('target')

    # Ignore name and state for this function
    kwargs.pop('name', None)
    kwargs.pop('state', None)

    for ignore in list(_STATE_INTERNAL_KEYWORDS) + ['chain', 'save', 'table']:
        if ignore in kwargs:
            del kwargs[ignore]

    rule = []
    proto = False
    bang_not_pat = re.compile(r'(!|not)\s?')

    def maybe_add_negation(arg):
        '''
        Will check if the defined argument is intended to be negated,
        (i.e. prefixed with '!' or 'not'), and add a '! ' to the rule.

        The prefix will be removed from the value in the kwargs dict.
        '''
        value = str(kwargs[arg])
        if value.startswith('!') or value.startswith('not'):
            kwargs[arg] = re.sub(bang_not_pat, '', value)
            return '! '
        return ''

    if 'if' in kwargs:
        rule.append('{0}-i {1}'.format(maybe_add_negation('if'), kwargs['if']))
        del kwargs['if']

    if 'of' in kwargs:
        rule.append('{0}-o {1}'.format(maybe_add_negation('of'), kwargs['of']))
        del kwargs['of']

    if 'proto' in kwargs:
        rule.append('{0}-p {1}'.format(maybe_add_negation('proto'), kwargs['proto']))
        proto = True
        del kwargs['proto']

    if 'match' in kwargs:
        match_value = kwargs['match']
        if not isinstance(match_value, list):
            match_value = match_value.split(',')
        for match in match_value:
            rule.append('-m {0}'.format(match))
            if 'name' in kwargs and match.strip() in ('pknock', 'quota2', 'recent'):
                rule.append('--name {0}'.format(kwargs['name']))
        del kwargs['match']

    if 'connstate' in kwargs:
        rule.append('{0}--state {1}'.format(maybe_add_negation('connstate'), kwargs['connstate']))
        del kwargs['connstate']

    if 'dport' in kwargs:
        rule.append('{0}--dport {1}'.format(maybe_add_negation('dport'), kwargs['dport']))
        del kwargs['dport']

    if 'sport' in kwargs:
        rule.append('{0}--sport {1}'.format(maybe_add_negation('sport'), kwargs['sport']))
        del kwargs['sport']

    for multiport_arg in ('dports', 'sports'):
        if multiport_arg in kwargs:
            if '-m multiport' not in rule:
                rule.append('-m multiport')
                if not proto:
                    return 'Error: proto must be specified'

            mp_value = kwargs[multiport_arg]
            if isinstance(mp_value, list):
                if any(i for i in mp_value if str(i).startswith('!') or str(i).startswith('not')):
                    mp_value = [re.sub(bang_not_pat, '', str(item)) for item in mp_value]
                    rule.append('!')
                dports = ','.join(str(i) for i in mp_value)
            else:
                if str(mp_value).startswith('!') or str(mp_value).startswith('not'):
                    dports = re.sub(bang_not_pat, '', mp_value)
                    rule.append('!')
                else:
                    dports = mp_value

            rule.append('--{0} {1}'.format(multiport_arg, dports))
            del kwargs[multiport_arg]

    if 'comment' in kwargs:
        rule.append('--comment "{0}"'.format(kwargs['comment']))
        del kwargs['comment']

    # --set in ipset is deprecated, works but returns error.
    # rewrite to --match-set if not empty, otherwise treat as recent option
    if 'set' in kwargs and kwargs['set']:
        rule.append('{0}--match-set {1}'.format(maybe_add_negation('set'), kwargs['set']))
        del kwargs['set']

    # Jumps should appear last, except for any arguments that are passed to
    # jumps, which of course need to follow.
    after_jump = []
    after_jump_arguments = (
        'jump',
        'j',
        'to-port',
        'to-ports',
        'to-destination',
        'to-source',
        'reject-with',
        'set-mark',
        'set-xmark',
        'log-level',
        'log-ip-options',
        'log-prefix',
        'log-tcp-options',
        'log-tcp-sequence',
    )
    for after_jump_argument in after_jump_arguments:
        if after_jump_argument in kwargs:
            value = kwargs[after_jump_argument]
            if len(str(value).split()) > 1:
                after_jump.append('--{0} "{1}"'.format(after_jump_argument, value))
            else:
                after_jump.append('--{0} {1}'.format(after_jump_argument, value))
            del kwargs[after_jump_argument]

    for item in kwargs:
        rule.append(maybe_add_negation(item))
        if len(item) == 1:
            rule.append('-{0} {1}'.format(item, kwargs[item]))
        else:
            rule.append('--{0} {1}'.format(item, kwargs[item]))

    rule += after_jump

    if full in ['True', 'true']:
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

        wait = '--wait' if _has_option('--wait', family) else ''

        return '{0} {1} -t {2} {3}{4} {5} {6} {7}'.format(_iptables_cmd(family),
               wait, table, flag, command, chain, position, ' '.join(rule))

    return ' '.join(rule)