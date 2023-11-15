    def _check_conflict(cls, dirPath, name):
        """
        Check whether the module of the given name conflicts with another module on the sys.path.

        :param dirPath: the directory from which the module was originally loaded
        :param name: the mpdule name
        """
        old_sys_path = sys.path
        try:
            sys.path = [d for d in old_sys_path if os.path.realpath(d) != os.path.realpath(dirPath)]
            try:
                colliding_module = importlib.import_module(name)
            except ImportError:
                pass
            else:
                raise ResourceException(
                    "The user module '%s' collides with module '%s from '%s'." % (
                        name, colliding_module.__name__, colliding_module.__file__))
        finally:
            sys.path = old_sys_path