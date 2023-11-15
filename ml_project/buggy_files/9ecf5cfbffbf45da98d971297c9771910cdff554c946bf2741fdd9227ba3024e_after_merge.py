    def update_config_data(self, defs=None, configfile=None):
        ''' really: update constants '''

        if defs is None:
            defs = self._base_defs

        if configfile is None:
            configfile = self._config_file

        if not isinstance(defs, dict):
            raise AnsibleOptionsError("Invalid configuration definition type: %s for %s" % (type(defs), defs))

        # update the constant for config file
        self.data.update_setting(Setting('CONFIG_FILE', configfile, '', 'string'))

        origin = None
        # env and config defs can have several entries, ordered in list from lowest to highest precedence
        for config in defs:
            if not isinstance(defs[config], dict):
                raise AnsibleOptionsError("Invalid configuration definition '%s': type is %s" % (to_native(config), type(defs[config])))

            # get value and origin
            try:
                value, origin = self.get_config_value_and_origin(config, configfile)
            except Exception as e:
                # when building constants.py we ignore invalid configs
                # CLI takes care of warnings once 'display' is loaded
                self.UNABLE[config] = to_text(e)
                continue

            # set the constant
            self.data.update_setting(Setting(config, value, origin, defs[config].get('type', 'string')))