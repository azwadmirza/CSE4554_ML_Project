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
                    if 'text/plain' in data:
                        view = ast.literal_eval(data['text/plain'])
                        self.sig_namespace_view.emit(view)
                    else:
                        view = None
                elif 'get_var_properties' in method:
                    properties = ast.literal_eval(data['text/plain'])
                    self.sig_var_properties.emit(properties)
                else:
                    if data is not None:
                        self._kernel_reply = ast.literal_eval(data['text/plain'])
                    else:
                        self._kernel_reply = None
                    self.sig_got_reply.emit()

                # Remove method after being processed
                self._kernel_methods.pop(expression)