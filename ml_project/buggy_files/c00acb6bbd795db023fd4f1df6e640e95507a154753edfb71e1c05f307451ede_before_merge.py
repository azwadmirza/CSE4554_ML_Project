def run(**kwargs):
    '''
    Run a single module function or a range of module functions in a batch.
    Supersedes ``module.run`` function, which requires ``m_`` prefix to
    function-specific parameters.

    :param returner:
        Specify a common returner for the whole batch to send the return data

    :param kwargs:
        Pass any arguments needed to execute the function(s)

    .. code-block:: yaml

      some_id_of_state:
        module.run:
          - network.ip_addrs:
            - interface: eth0
          - cloud.create:
            - names:
              - test-isbm-1
              - test-isbm-2
            - ssh_username: sles
            - image: sles12sp2
            - securitygroup: default
            - size: 'c3.large'
            - location: ap-northeast-1
            - delvol_on_destroy: True


    :return:
    '''

    if 'name' in kwargs:
        kwargs.pop('name')
    ret = {
        'name': kwargs.keys(),
        'changes': {},
        'comment': '',
        'result': None,
    }

    functions = [func for func in kwargs.keys() if '.' in func]
    missing = []
    tests = []
    for func in functions:
        func = func.split(':')[0]
        if func not in __salt__:
            missing.append(func)
        elif __opts__['test']:
            tests.append(func)

    if tests or missing:
        ret['comment'] = ' '.join([
            missing and "Unavailable function{plr}: "
                        "{func}.".format(plr=(len(missing) > 1 or ''),
                                         func=(', '.join(missing) or '')) or '',
            tests and "Function{plr} {func} to be "
                      "executed.".format(plr=(len(tests) > 1 or ''),
                                         func=(', '.join(tests)) or '') or '',
        ]).strip()
        ret['result'] = not (missing or not tests)

    if ret['result'] is None:
        ret['result'] = True

        failures = []
        success = []
        for func in functions:
            _func = func.split(':')[0]
            try:
                func_ret = _call_function(_func, returner=kwargs.get('returner'),
                                          func_args=kwargs.get(func))
                if not _get_result(func_ret, ret['changes'].get('ret', {})):
                    if isinstance(func_ret, dict):
                        failures.append("'{0}' failed: {1}".format(
                            func, func_ret.get('comment', '(error message N/A)')))
                else:
                    success.append('{0}: {1}'.format(
                        func, func_ret.get('comment', 'Success') if isinstance(func_ret, dict) else func_ret))
                    ret['changes'][func] = func_ret
            except (SaltInvocationError, TypeError) as ex:
                failures.append("'{0}' failed: {1}".format(func, ex))
        ret['comment'] = ', '.join(failures + success)
        ret['result'] = not bool(failures)

    return ret