    def get_config_value(self, config, cfile=None, plugin_type=None, plugin_name=None, keys=None, variables=None):
        ''' wrapper '''
        value, _drop = self.get_config_value_and_origin(config, cfile=cfile, plugin_type=plugin_type, plugin_name=plugin_name, keys=keys, variables=variables)
        return value