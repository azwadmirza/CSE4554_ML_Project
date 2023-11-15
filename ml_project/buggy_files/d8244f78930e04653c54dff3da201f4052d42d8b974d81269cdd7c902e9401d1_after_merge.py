def runner(opts):
    '''
    Directly call a function inside a loader directory
    '''
    ret = LazyLoader(_module_dirs(opts, 'runners', 'runner', ext_type_dirs='runner_dirs'),
                     opts,
                     tag='runners',
                     )
    # TODO: change from __salt__ to something else, we overload __salt__ too much
    ret.pack['__salt__'] = ret
    return ret