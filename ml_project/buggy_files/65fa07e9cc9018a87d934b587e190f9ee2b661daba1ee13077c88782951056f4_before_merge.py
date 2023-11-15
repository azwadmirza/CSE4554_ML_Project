    def __call__(self, function):
        '''
        The decorator is "__call__"d with the function, we take that function
        and determine which module and function name it is to store in the
        class wide depandancy_dict
        '''
        try:
            # This inspect call may fail under certain conditions in the loader. Possibly related to
            # a Python bug here:
            # http://bugs.python.org/issue17735
            frame = inspect.stack()[1][0]
            # due to missing *.py files under esky we cannot use inspect.getmodule
            # module name is something like salt.loaded.int.modules.test
            kind = frame.f_globals['__name__'].rsplit('.', 2)[1]
            for dep in self.dependencies:
                self.dependency_dict[kind][dep].add(
                    (frame, function, self.fallback_function)
                )
        except Exception as exc:
            log.error('Exception encountered when attempting to inspect frame in '
                      'dependency decorator: {0}'.format(exc))
        return function