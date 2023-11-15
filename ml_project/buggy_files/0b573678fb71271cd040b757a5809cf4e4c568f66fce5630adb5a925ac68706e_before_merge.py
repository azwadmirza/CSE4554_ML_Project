    def read(self):
        '''
        Read in the specified map file and return the map structure
        '''
        if self.opts.get('map', None) is None:
            return {}

        if not os.path.isfile(self.opts['map']):
            log.error(
                'The specified map file does not exist: \'{0}\''.format(
                    self.opts['map'])
            )
            raise SaltCloudNotFound()
        try:
            renderer = self.opts.get('renderer', 'yaml_jinja')
            rend = salt.loader.render(self.opts, {})
            map_ = compile_template(
                self.opts['map'], rend, renderer
            )
        except Exception as exc:
            log.error(
                'Rendering map {0} failed, render error:\n{1}'.format(
                    self.opts['map'], exc
                ),
                exc_info_on_loglevel=logging.DEBUG
            )
            return {}

        if 'include' in map_:
            map_ = salt.config.include_config(
                map_, self.opts['map'], verbose=False
            )

        # Create expected data format if needed
        for profile, mapped in map_.copy().items():
            if isinstance(mapped, (list, tuple)):
                entries = {}
                for mapping in mapped:
                    if isinstance(mapping, string_types):
                        # Foo:
                        #   - bar1
                        #   - bar2
                        mapping = {mapping: None}
                    for name, overrides in mapping.items():
                        if overrides is None:
                            # Foo:
                            #   - bar1:
                            #   - bar2:
                            overrides = {}
                        overrides.setdefault('name', name)
                        entries[name] = overrides
                map_[profile] = entries
                continue

            if isinstance(mapped, dict):
                # Convert the dictionary mapping to a list of dictionaries
                # Foo:
                #  bar1:
                #    grains:
                #      foo: bar
                #  bar2:
                #    grains:
                #      foo: bar
                entries = {}
                for name, overrides in mapped.items():
                    overrides.setdefault('name', name)
                    entries[name] = overrides
                map_[profile] = entries
                continue

            if isinstance(mapped, string_types):
                # If it's a single string entry, let's make iterable because of
                # the next step
                mapped = [mapped]

            map_[profile] = {}
            for name in mapped:
                map_[profile][name] = {'name': name}
        return map_