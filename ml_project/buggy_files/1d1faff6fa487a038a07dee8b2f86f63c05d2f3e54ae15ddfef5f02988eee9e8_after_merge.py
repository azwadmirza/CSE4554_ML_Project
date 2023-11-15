def _validate_opts(opts):
    '''
    Check that all of the types of values passed into the config are
    of the right types
    '''
    def format_multi_opt(valid_type):
        try:
            num_types = len(valid_type)
        except TypeError:
            # Bare type name won't have a length, return the name of the type
            # passed.
            return valid_type.__name__
        else:
            def get_types(types, type_tuple):
                for item in type_tuple:
                    if isinstance(item, tuple):
                        get_types(types, item)
                    else:
                        try:
                            types.append(item.__name__)
                        except AttributeError:
                            log.warning(
                                'Unable to interpret type %s while validating '
                                'configuration', item
                            )
            types = []
            get_types(types, valid_type)

            ret = ', '.join(types[:-1])
            ret += ' or ' + types[-1]
            return ret

    errors = []

    err = ('Key \'{0}\' with value {1} has an invalid type of {2}, a {3} is '
           'required for this value')
    for key, val in six.iteritems(opts):
        if key in VALID_OPTS:
            if isinstance(val, VALID_OPTS[key]):
                continue

            if hasattr(VALID_OPTS[key], '__call__'):
                try:
                    VALID_OPTS[key](val)
                    if isinstance(val, (list, dict)):
                        # We'll only get here if VALID_OPTS[key] is str or
                        # bool, and the passed value is a list/dict. Attempting
                        # to run int() or float() on a list/dict will raise an
                        # exception, but running str() or bool() on it will
                        # pass despite not being the correct type.
                        errors.append(
                            err.format(
                                key,
                                val,
                                type(val).__name__,
                                VALID_OPTS[key].__name__
                            )
                        )
                except (TypeError, ValueError):
                    errors.append(
                        err.format(key,
                                   val,
                                   type(val).__name__,
                                   VALID_OPTS[key].__name__)
                    )
                continue

            errors.append(
                err.format(key,
                           val,
                           type(val).__name__,
                           format_multi_opt(VALID_OPTS[key]))
            )

    # RAET on Windows uses 'win32file.CreateMailslot()' for IPC. Due to this,
    # sock_dirs must start with '\\.\mailslot\' and not contain any colons.
    # We don't expect the user to know this, so we will fix up their path for
    # them if it isn't compliant.
    if (salt.utils.is_windows() and opts.get('transport') == 'raet' and
             'sock_dir' in opts and
             not opts['sock_dir'].startswith('\\\\.\\mailslot\\')):
        opts['sock_dir'] = (
                '\\\\.\\mailslot\\' + opts['sock_dir'].replace(':', ''))

    for error in errors:
        log.warning(error)
    if errors:
        return False
    return True