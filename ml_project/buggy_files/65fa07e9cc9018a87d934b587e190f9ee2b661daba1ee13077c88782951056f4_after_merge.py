    def __call__(self, function):
        '''
        Callable method of the decorator object when
        the decorated function is gets called.

        :param function:
        :return:
        '''
        _DeprecationDecorator.__call__(self, function)

        def _decorate(*args, **kwargs):
            '''
            Decorator function.

            :param args:
            :param kwargs:
            :return:
            '''
            self._set_function(function)
            if self._is_used_deprecated():
                if self._curr_version < self._exp_version:
                    msg = list()
                    if self._with_name:
                        msg.append('The function "{f_name}" is deprecated and will '
                                   'expire in version "{version_name}".'.format(
                                       f_name=self._with_name.startswith("_") and self._orig_f_name or self._with_name,
                                       version_name=self._exp_version_name))
                    else:
                        msg.append('The function is using its deprecated version and will '
                                   'expire in version "{version_name}".'.format(version_name=self._exp_version_name))
                    msg.append('Use its successor "{successor}" instead.'.format(successor=self._orig_f_name))
                    log.warning(' '.join(msg))
                else:
                    msg_patt = 'The lifetime of the function "{f_name}" expired.'
                    if '_' + self._orig_f_name == self._function.func_name:
                        msg = [msg_patt.format(f_name=self._orig_f_name),
                               'Please turn off its deprecated version in the configuration']
                    else:
                        msg = ['Although function "{f_name}" is called, an alias "{f_alias}" '
                               'is configured as its deprecated version.'.format(
                                   f_name=self._orig_f_name, f_alias=self._with_name or self._orig_f_name),
                               msg_patt.format(f_name=self._with_name or self._orig_f_name),
                               'Please use its successor "{successor}" instead.'.format(successor=self._orig_f_name)]
                    log.error(' '.join(msg))
                    raise CommandExecutionError(' '.join(msg))
            return self._call_function(kwargs)

        _decorate.__doc__ = self._function.__doc__
        return _decorate