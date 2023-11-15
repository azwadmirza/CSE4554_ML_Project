    def __rpc__(self, name, *args, **kwargs):
        """Executes the json-rpc and returns the output received
           from remote device.
           :name: rpc method to be executed over connection plugin that implements jsonrpc 2.0
           :args: Ordered list of params passed as arguments to rpc method
           :kwargs: Dict of valid key, value pairs passed as arguments to rpc method

           For usage refer the respective connection plugin docs.
        """
        self.check_rc = kwargs.pop('check_rc', True)
        self.ignore_warning = kwargs.pop('ignore_warning', True)

        response = self._exec_jsonrpc(name, *args, **kwargs)
        if 'error' in response:
            rpc_error = response['error'].get('data')
            return self.parse_rpc_error(to_native(rpc_error, errors='surrogate_then_replace'))

        return fromstring(to_native(response['result'], errors='surrogate_then_replace'))