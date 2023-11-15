    def get_config_value_and_origin(self, config, cfile=None, plugin_type=None, plugin_name=None, keys=None, variables=None):
        ''' Given a config key figure out the actual value and report on the origin of the settings '''

        if cfile is None:
            # use default config
            cfile = self._config_file

        # Note: sources that are lists listed in low to high precedence (last one wins)
        value = None
        origin = None
        defs = {}
        if plugin_type is None:
            defs = self._base_defs
        elif plugin_name is None:
            defs = self._plugins[plugin_type]
        else:
            defs = self._plugins[plugin_type][plugin_name]

        if config in defs:
            # Use 'variable overrides' if present, highest precedence, but only present when querying running play
            if variables and defs[config].get('vars'):
                value, origin = self._loop_entries(variables, defs[config]['vars'])
                origin = 'var: %s' % origin

            # use playbook keywords if you have em
            if value is None and keys:
                value, origin = self._loop_entries(keys, defs[config]['keywords'])
                origin = 'keyword: %s' % origin

            # env vars are next precedence
            if value is None and defs[config].get('env'):
                value, origin = self._loop_entries(os.environ, defs[config]['env'])
                origin = 'env: %s' % origin

            # try config file entries next, if we have one
            if self._parsers.get(cfile, None) is None:
                self._parse_config_file(cfile)

            if value is None and cfile is not None:
                ftype = get_config_type(cfile)
                if ftype and defs[config].get(ftype):
                    if ftype == 'ini':
                        # load from ini config
                        try:  # FIXME: generalize _loop_entries to allow for files also, most of this code is dupe
                            for ini_entry in defs[config]['ini']:
                                temp_value = get_ini_config_value(self._parsers[cfile], ini_entry)
                                if temp_value is not None:
                                    value = temp_value
                                    origin = cfile
                                    if 'deprecated' in ini_entry:
                                        self.DEPRECATED.append(('[%s]%s' % (ini_entry['section'], ini_entry['key']), ini_entry['deprecated']))
                        except Exception as e:
                            sys.stderr.write("Error while loading ini config %s: %s" % (cfile, to_native(e)))
                    elif ftype == 'yaml':
                        # FIXME: implement, also , break down key from defs (. notation???)
                        origin = cfile

            # set default if we got here w/o a value
            if value is None:
                if defs[config].get('required', False):
                    entry = ''
                    if plugin_type:
                        entry += 'plugin_type: %s ' % plugin_type
                        if plugin_name:
                            entry += 'plugin: %s ' % plugin_name
                    entry += 'setting: %s ' % config
                    raise AnsibleError("No setting was provided for required configuration %s" % (entry))
                else:
                    value = defs[config].get('default')
                    origin = 'default'
                    # skip typing as this is a temlated default that will be resolved later in constants, which has needed vars
                    if plugin_type is None and isinstance(value, string_types) and (value.startswith('{{') and value.endswith('}}')):
                        return value, origin

            # ensure correct type, can raise exceptoins on mismatched types
            value = ensure_type(value, defs[config].get('type'), origin=origin)

            # deal with deprecation of the setting
            if 'deprecated' in defs[config] and origin != 'default':
                self.DEPRECATED.append((config, defs[config].get('deprecated')))
        else:
            raise AnsibleError('Requested option %s was not defined in configuration' % to_native(config))

        return value, origin