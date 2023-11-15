def runner(name, **kwargs):
    '''
    Execute a runner module on the master

    .. versionadded:: 2014.7.0

    name
        The name of the function to run
    kwargs
        Any keyword arguments to pass to the runner function

    .. code-block:: yaml

         run-manage-up:
          salt.runner:
            - name: manage.up
    '''
    try:
        jid = __orchestration_jid__
    except NameError:
        log.debug(
            'Unable to fire args event due to missing __orchestration_jid__'
        )
        jid = None
    out = __salt__['saltutil.runner'](name,
                                      __orchestration_jid__=jid,
                                      __env__=__env__,
                                      full_return=True,
                                      **kwargs)

    runner_return = out.get('return')
    if 'success' in out and not out['success']:
        ret = {
            'name': name,
            'result': False,
            'changes': {},
            'comment': runner_return if runner_return else "Runner function '{0}' failed without comment.".format(name)
        }
    else:
        ret = {
            'name': name,
            'result': True,
            'changes': runner_return if runner_return else {},
            'comment': "Runner function '{0}' executed.".format(name)
        }

    ret['__orchestration__'] = True
    if 'jid' in out:
        ret['__jid__'] = out['jid']

    return ret