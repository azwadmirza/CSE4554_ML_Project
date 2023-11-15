    def get_config_value(self, config, cfile=None, plugin_type=None, plugin_name=None, keys=None, variables=None):
        ''' wrapper '''

        try:
            value, _drop = self.get_config_value_and_origin(config, cfile=cfile, plugin_type=plugin_type, plugin_name=plugin_name,
                                                            keys=keys, variables=variables)
        except Exception as e:
            raise AnsibleError("Invalid settings supplied for %s: %s" % (config, to_native(e)))
        return value