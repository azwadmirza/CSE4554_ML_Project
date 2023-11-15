def runner(opts):
    '''
    Directly call a function inside a loader directory
    '''
    return LazyLoader(_module_dirs(opts, 'runners', 'runner', ext_type_dirs='runner_dirs'),
                     opts,
                     tag='runners',
                     pack={'__salt__': minion_mods(opts)},
                     )