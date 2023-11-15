    def as_dict(self, attrs=None, ad_value=None):
        """Utility method returning process information as a
        hashable dictionary.

        If 'attrs' is specified it must be a list of strings
        reflecting available Process class' attribute names
        (e.g. ['cpu_times', 'name']) else all public (read
        only) attributes are assumed.

        'ad_value' is the value which gets assigned in case
        AccessDenied  exception is raised when retrieving that
        particular process information.
        """
        excluded_names = set(
            ['send_signal', 'suspend', 'resume', 'terminate', 'kill', 'wait',
             'is_running', 'as_dict', 'parent', 'children', 'rlimit'])
        retdict = dict()
        ls = set(attrs or [x for x in dir(self) if not x.startswith('get')])
        for name in ls:
            if name.startswith('_'):
                continue
            if name.startswith('set_'):
                continue
            if name.startswith('get_'):
                msg = "%s() is deprecated; use %s() instead" % (name, name[4:])
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                name = name[4:]
                if name in ls:
                    continue
            if name == 'getcwd':
                msg = "getcwd() is deprecated; use cwd() instead"
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                name = 'cwd'
                if name in ls:
                    continue

            if name in excluded_names:
                continue
            try:
                attr = getattr(self, name)
                if callable(attr):
                    ret = attr()
                else:
                    ret = attr
            except AccessDenied:
                ret = ad_value
            except NotImplementedError:
                # in case of not implemented functionality (may happen
                # on old or exotic systems) we want to crash only if
                # the user explicitly asked for that particular attr
                if attrs:
                    raise
                continue
            retdict[name] = ret
        return retdict