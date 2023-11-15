        def _delayed_create(create_opts, datasets):
            LOG.debug("create_opts: %s", create_opts)
            try:
                if 'platform_name' not in kwargs:
                    kwargs['platform_name'] = datasets.attrs['platform_name']
                if 'name' not in kwargs:
                    kwargs['name'] = datasets[0].attrs['name']
                if 'start_time' not in kwargs:
                    kwargs['start_time'] = datasets[0].attrs['start_time']
                if 'sensor' not in kwargs:
                    kwargs['sensor'] = datasets[0].attrs['sensor']

                try:
                    self.mitiff_config[kwargs['sensor']] = datasets['metadata_requirements']['config']
                    self.translate_channel_name[kwargs['sensor']] = datasets['metadata_requirements']['translate']
                    self.channel_order[kwargs['sensor']] = datasets['metadata_requirements']['order']
                    self.file_pattern = datasets['metadata_requirements']['file_pattern']
                except KeyError:
                    # For some mitiff products this info is needed, for others not.
                    # If needed you should know how to fix this
                    pass

                image_description = self._make_image_description(datasets, **kwargs)
                LOG.debug("File pattern %s", self.file_pattern)
                if isinstance(datasets, list):
                    kwargs['start_time'] = datasets[0].attrs['start_time']
                else:
                    kwargs['start_time'] = datasets.attrs['start_time']
                gen_filename = filename or self.get_filename(**kwargs)
                LOG.info("Saving mitiff to: %s ...", gen_filename)
                self._save_datasets_as_mitiff(datasets, image_description, gen_filename, **kwargs)
            except:
                raise