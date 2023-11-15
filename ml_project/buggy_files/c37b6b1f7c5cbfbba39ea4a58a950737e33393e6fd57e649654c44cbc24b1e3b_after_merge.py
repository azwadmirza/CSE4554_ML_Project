    def open_std_fd(fdname):
        # fdname is 'stdout' or 'stderr'
        stdfspec = kwargs.get(fdname)  # spec is str name or tuple (name, mode)
        if stdfspec is None:
            return None
        elif isinstance(stdfspec, str):
            fname = stdfspec
            mode = 'a+'
        elif isinstance(stdfspec, tuple):
            if len(stdfspec) != 2:
                raise pe.BadStdStreamFile("std descriptor %s has incorrect tuple length %s" % (fdname, len(stdfspec)), TypeError('Bad Tuple Length'))
            fname, mode = stdfspec
        else:
            raise pe.BadStdStreamFile("std descriptor %s has unexpected type %s" % (fdname, str(type(stdfspec))), TypeError('Bad Tuple Type'))

        try:
            if os.path.dirname(fname):
                os.makedirs(os.path.dirname(fname), exist_ok=True)
            fd = open(fname, mode)
        except Exception as e:
            raise pe.BadStdStreamFile(fname, e)
        return fd