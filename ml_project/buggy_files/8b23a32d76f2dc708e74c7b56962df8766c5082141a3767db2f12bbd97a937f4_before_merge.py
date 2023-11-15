def list_functions(module=''):
    '''
    List the functions for all modules. Optionally, specify a module to list
    from.

    CLI Example::

        salt '*' sys.list_functions
        salt '*' sys.list_functions sys
    '''
    names = set()
    if module:
        # allow both "sys" and "sys." to match sys, without also matching
        # sysctl
        module = module + '.' if not module.endswith('.') else module
    for func in __salt__:
        if func.startswith(module):
            names.add(func)
    return sorted(names)