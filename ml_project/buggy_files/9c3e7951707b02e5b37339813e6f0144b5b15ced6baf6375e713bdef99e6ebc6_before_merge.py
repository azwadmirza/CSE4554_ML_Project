    def wrapped(*args, **kwargs):
        start_time = time.time()
        ret = function(*args, **salt.utils.args.clean_kwargs(**kwargs))
        end_time = time.time()
        if function.__module__.startswith('salt.loaded.int.'):
            mod_name = function.__module__[16:]
        else:
            mod_name = function.__module__
        fstr = 'Function %s.%s took %.{0}f seconds to execute'.format(
            sys.float_info.dig
        )
        log.profile(fstr, mod_name, function.__name__, end_time - start_time)
        return ret