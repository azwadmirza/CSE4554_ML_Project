def function(
        name,
        tgt,
        ssh=False,
        tgt_type=None,
        expr_form=None,
        ret='',
        expect_minions=False,
        fail_minions=None,
        fail_function=None,
        arg=None,
        kwarg=None,
        timeout=None,
        batch=None):
    '''
    Execute a single module function on a remote minion via salt or salt-ssh

    name
        The name of the function to run, aka cmd.run or pkg.install

    tgt
        The target specification, aka '*' for all minions

    tgt_type | expr_form
        The target type, defaults to glob

    arg
        The list of arguments to pass into the function

    kwarg
        The list of keyword arguments to pass into the function

    ret
        Optionally set a single or a list of returners to use

    expect_minions
        An optional boolean for failing if some minions do not respond

    fail_minions
        An optional list of targeted minions where failure is an option

    fail_function
        An optional string that points to a salt module that returns True or False
        based on the returned data dict for individual minions

    ssh
        Set to `True` to use the ssh client instead of the standard salt client
    '''
    func_ret = {'name': name,
           'changes': {},
           'comment': '',
           'result': True}
    if kwarg is None:
        kwarg = {}
    if isinstance(arg, str):
        func_ret['warnings'] = ['Please specify \'arg\' as a list, not a string. '
                           'Modifying in place, but please update SLS file '
                           'to remove this warning.']
        arg = arg.split()

    cmd_kw = {'arg': arg or [], 'kwarg': kwarg, 'ret': ret, 'timeout': timeout}

    if expr_form and tgt_type:
        func_ret['warnings'] = [
            'Please only use \'tgt_type\' or \'expr_form\' not both. '
            'Preferring \'tgt_type\' over \'expr_form\''
        ]
        expr_form = None
    elif expr_form and not tgt_type:
        tgt_type = expr_form
    elif not tgt_type and not expr_form:
        tgt_type = 'glob'

    if batch is not None:
        cmd_kw['batch'] = str(batch)

    cmd_kw['expr_form'] = tgt_type
    cmd_kw['ssh'] = ssh
    cmd_kw['expect_minions'] = expect_minions
    cmd_kw['_cmd_meta'] = True
    fun = name
    if __opts__['test'] is True:
        func_ret['comment'] = (
                'Function {0} will be executed on target {1} as test={2}'
                ).format(fun, tgt, str(False))
        func_ret['result'] = None
        return func_ret
    try:
        cmd_ret = __salt__['saltutil.cmd'](tgt, fun, **cmd_kw)
    except Exception as exc:
        func_ret['result'] = False
        func_ret['comment'] = str(exc)
        return func_ret

    changes = {}
    fail = set()
    failures = {}

    if fail_minions is None:
        fail_minions = ()
    elif isinstance(fail_minions, string_types):
        fail_minions = [minion.strip() for minion in fail_minions.split(',')]
    elif not isinstance(fail_minions, list):
        func_ret.setdefault('warnings', []).append(
            '\'fail_minions\' needs to be a list or a comma separated '
            'string. Ignored.'
        )
        fail_minions = ()
    for minion, mdata in six.iteritems(cmd_ret):
        m_ret = False
        if mdata.get('retcode'):
            func_ret['result'] = False
            fail.add(minion)
        if mdata.get('failed', False):
            m_func = False
        else:
            if 'return' in mdata and 'ret' not in mdata:
                mdata['ret'] = mdata.pop('return')
            m_ret = mdata['ret']
            m_func = (not fail_function and True) or __salt__[fail_function](m_ret)

        if not m_func:
            if minion not in fail_minions:
                fail.add(minion)
            failures[minion] = m_ret and m_ret or 'Minion did not respond'
            continue
        changes[minion] = m_ret
    if not cmd_ret:
        func_ret['result'] = False
        func_ret['command'] = 'No minions responded'
    else:
        if changes:
            func_ret['changes'] = {'out': 'highstate', 'ret': changes}
        if fail:
            func_ret['result'] = False
            func_ret['comment'] = 'Running function {0} failed on minions: {1}'.format(name, ', '.join(fail))
        else:
            func_ret['comment'] = 'Function ran successfully.'
        if changes:
            func_ret['comment'] += ' Function {0} ran on {1}.'.format(name, ', '.join(changes))
        if failures:
            func_ret['comment'] += '\nFailures:\n'
            for minion, failure in six.iteritems(failures):
                func_ret['comment'] += '\n'.join(
                        (' ' * 4 + l)
                        for l in salt.output.out_format(
                            {minion: failure},
                            'highstate',
                            __opts__,
                            ).splitlines()
                        )
                func_ret['comment'] += '\n'
    return func_ret