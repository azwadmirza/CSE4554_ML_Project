    def return_user_exc(self, builder, exc, exc_args=None, loc=None,
                        func_name=None):
        if exc is not None and not issubclass(exc, BaseException):
            raise TypeError("exc should be None or exception class, got %r"
                            % (exc,))
        if exc_args is not None and not isinstance(exc_args, tuple):
            raise TypeError("exc_args should be None or tuple, got %r"
                            % (exc_args,))
        # None is indicative of no args, set the exc_args to an empty tuple
        # as PyObject_CallObject(exc, exc_args) requires the second argument to
        # be a tuple (or nullptr, but doing this makes it consistent)
        if exc_args is None:
            exc_args = tuple()

        pyapi = self.context.get_python_api(builder)
        # Build excinfo struct
        if loc is not None:
            fname = loc._raw_function_name()
            if fname is None:
                # could be exec(<string>) or REPL, try func_name
                fname = func_name

            locinfo = (fname, loc.filename, loc.line)
            if None in locinfo:
                locinfo = None
        else:
            locinfo = None
        exc = (exc, exc_args, locinfo)
        struct_gv = pyapi.serialize_object(exc)
        excptr = self._get_excinfo_argument(builder.function)
        builder.store(struct_gv, excptr)
        self._return_errcode_raw(builder, RETCODE_USEREXC)