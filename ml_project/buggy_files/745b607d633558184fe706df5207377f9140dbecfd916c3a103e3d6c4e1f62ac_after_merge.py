    def __getattribute__(self, name):
        if name in _LOCAL_ATTRS:
            # never proxy special attributes, always get them from the class type
            return super().__getattribute__(name)
        else:
            try:
                # Go for proxying class-level attributes first;
                # make sure to check for attribute in self.__dict__ to get the class-level
                # attribute from the class itself, not from some of its parent classes.
                res = super().__getattribute__("__dict__")[name]
            except KeyError:
                # Class-level attribute not found in the class itself; it might be present
                # in its parents, but we must first see if we should go to a remote
                # end, because in "remote context" local attributes are only those which
                # are explicitly allowed by being defined in the class itself.
                frame = sys._getframe()
                try:
                    is_inspect = frame.f_back.f_code.co_filename == inspect.__file__
                except AttributeError:
                    is_inspect = False
                finally:
                    del frame
                if is_inspect:
                    # be always-local for inspect.* functions
                    return super().__getattribute__(name)
                else:
                    try:
                        remote = self.__real_cls__.__wrapper_remote__
                    except AttributeError:
                        # running in local mode, fall back
                        return super().__getattribute__(name)
                    return getattr(remote, name)
            else:
                try:
                    # note that any attribute might be in fact a data descriptor,
                    # account for that; we only need it for attributes we get from __dict__[],
                    # because other cases are handled by super().__getattribute__ for us
                    getter = res.__get__
                except AttributeError:
                    return res
                return getter(None, self)