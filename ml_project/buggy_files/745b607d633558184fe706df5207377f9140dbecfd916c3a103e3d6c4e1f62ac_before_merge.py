    def __getattribute__(self, name):
        if name in _LOCAL_ATTRS:
            # never proxy special attributes, always get them from the class type
            res = object.__getattribute__(self, name)
        else:
            try:
                # Go for proxying class-level attributes first;
                # make sure to check for attribute in self.__dict__ to get the class-level
                # attribute from the class itself, not from some of its parent classes.
                # Also note we use object.__getattribute__() to skip any potential
                # class-level __getattr__
                res = object.__getattribute__(self, "__dict__")[name]
            except KeyError:
                try:
                    res = object.__getattribute__(self, name)
                except AttributeError:
                    frame = sys._getframe()
                    try:
                        is_inspect = frame.f_back.f_code.co_filename == inspect.__file__
                    except AttributeError:
                        is_inspect = False
                    finally:
                        del frame
                    if is_inspect:
                        # be always-local for inspect.* functions
                        res = super().__getattribute__(name)
                    else:
                        try:
                            remote = object.__getattribute__(
                                object.__getattribute__(self, "__real_cls__"),
                                "__wrapper_remote__",
                            )
                        except AttributeError:
                            # running in local mode, fall back
                            res = super().__getattribute__(name)
                        else:
                            res = getattr(remote, name)
        try:
            # note that any attribute might be in fact a data descriptor,
            # account for that
            getter = res.__get__
        except AttributeError:
            return res
        return getter(None, self)