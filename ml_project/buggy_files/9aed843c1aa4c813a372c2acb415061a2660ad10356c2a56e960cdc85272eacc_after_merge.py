    def get_capabilities(self):
        result = {}
        result['rpc'] = self.get_base_rpc()
        result['device_info'] = self.get_device_info()
        if isinstance(self._connection, NetworkCli):
            result['network_api'] = 'cliconf'
        else:
            result['network_api'] = 'eapi'
        return json.dumps(result)