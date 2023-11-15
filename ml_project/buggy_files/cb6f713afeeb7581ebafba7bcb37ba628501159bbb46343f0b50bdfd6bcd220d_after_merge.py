def set_environ(varname, path):
    """Define an environment variable for use in CleanerML and Winapp2.ini"""
    if not path:
        return
    if varname in os.environ:
        #logger.debug('set_environ(%s, %s): skipping because environment variable is already defined', varname, path)
        if 'nt' == os.name:
            os.environ[varname] = bleachbit.expandvars(u'%%%s%%' % varname).encode('utf-8')
        # Do not redefine the environment variable when it already exists
        # But re-encode them with utf-8 instead of mbcs
        return
    try:
        if not os.path.exists(path):
            raise RuntimeError('Variable %s points to a non-existent path %s' % (varname, path))
        os.environ[varname] = path if isinstance(path, str) else path.encode('utf8')
    except:
        logger.exception('set_environ(%s, %s): exception when setting environment variable', varname, path)