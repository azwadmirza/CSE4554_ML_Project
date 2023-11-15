    def import_object(self, raiseerror: bool = False) -> bool:
        def is_valid_module_all(__all__: Any) -> bool:
            """Check the given *__all__* is valid for a module."""
            if (isinstance(__all__, (list, tuple)) and
                    all(isinstance(e, str) for e in __all__)):
                return True
            else:
                return False

        ret = super().import_object(raiseerror)

        if not self.options.ignore_module_all:
            __all__ = getattr(self.object, '__all__', None)
            if is_valid_module_all(__all__):
                # valid __all__ found. copy it to self.__all__
                self.__all__ = __all__
            elif __all__:
                # invalid __all__ found.
                logger.warning(__('__all__ should be a list of strings, not %r '
                                  '(in module %s) -- ignoring __all__') %
                               (__all__, self.fullname), type='autodoc')

        return ret