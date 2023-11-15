def __virtual__():
    '''
    Only load if the dockerng execution module is available
    '''
    if 'dockerng.version' in __salt__:
        global _validate_input  # pylint: disable=global-statement
        _validate_input = salt.utils.namespaced_function(
            _validate_input, globals()
        )
        return __virtualname__
    return (False, __salt__.missing_fun_string('dockerng.version'))