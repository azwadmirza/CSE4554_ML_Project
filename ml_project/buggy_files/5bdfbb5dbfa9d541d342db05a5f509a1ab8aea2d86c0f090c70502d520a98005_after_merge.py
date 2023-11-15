    def __call__(self, function):
        '''
        Callable method of the decorator object when
        the decorated function is gets called.

        :param function:
        :return:
        '''
        _DeprecationDecorator.__call__(self, function)

        @wraps(function)
        def _decorate(*args, **kwargs):
            '''
            Decorator function.

            :param args:
            :param kwargs:
            :return:
            '''
            if self._curr_version < self._exp_version:
                msg = ['The function "{f_name}" is deprecated and will '
                       'expire in version "{version_name}".'.format(f_name=self._function.__name__,
                                                                    version_name=self._exp_version_name)]
                if self._successor:
                    msg.append('Use successor "{successor}" instead.'.format(successor=self._successor))
                log.warning(' '.join(msg))
            else:
                msg = ['The lifetime of the function "{f_name}" expired.'.format(f_name=self._function.__name__)]
                if self._successor:
                    msg.append('Please use its successor "{successor}" instead.'.format(successor=self._successor))
                log.warning(' '.join(msg))
                raise CommandExecutionError(' '.join(msg))
            return self._call_function(kwargs)
        return _decorate