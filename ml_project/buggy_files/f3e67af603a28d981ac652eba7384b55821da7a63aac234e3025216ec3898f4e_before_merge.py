    def handle_exec_method(self, msg):
        """
        Handle data returned by silent executions of kernel methods

        This is based on the _handle_exec_callback of RichJupyterWidget.
        Therefore this is licensed BSD.
        """
        user_exp = msg['content'].get('user_expressions')
        if not user_exp:
            return
        for expression in user_exp:
            if expression in self._kernel_methods:
                # Process kernel reply
                method = self._kernel_methods[expression]
                reply = user_exp[expression]
                data = reply.get('data')
                if 'get_namespace_view' in method:
                    if data is not None and 'text/plain' in data:
                        view = ast.literal_eval(data['text/plain'])
                    else:
                        view = None
                    self.sig_namespace_view.emit(view)
                elif 'get_var_properties' in method:
                    if data is not None and 'text/plain' in data:
                        properties = ast.literal_eval(data['text/plain'])
                    else:
                        properties = None
                    self.sig_var_properties.emit(properties)
                elif 'get_cwd' in method:
                    if data is not None and 'text/plain' in data:
                        self._cwd = ast.literal_eval(data['text/plain'])
                        if PY2:
                            self._cwd = encoding.to_unicode_from_fs(self._cwd)
                    else:
                        self._cwd = ''
                    self.sig_change_cwd.emit(self._cwd)
                elif 'get_syspath' in method:
                    if data is not None and 'text/plain' in data:
                        syspath = ast.literal_eval(data['text/plain'])
                    else:
                        syspath = None
                    self.sig_show_syspath.emit(syspath)
                elif 'get_env' in method:
                    if data is not None and 'text/plain' in data:
                        env = ast.literal_eval(data['text/plain'])
                    else:
                        env = None
                    self.sig_show_env.emit(env)
                elif 'getattr' in method:
                    if data is not None and 'text/plain' in data:
                        is_spyder_kernel = data['text/plain']
                        if 'SpyderKernel' in is_spyder_kernel:
                            self.sig_is_spykernel.emit(self)
                else:
                    if data is not None and 'text/plain' in data:
                        self._kernel_reply = ast.literal_eval(data['text/plain'])
                    else:
                        self._kernel_reply = None
                    self.sig_got_reply.emit()

                # Remove method after being processed
                self._kernel_methods.pop(expression)