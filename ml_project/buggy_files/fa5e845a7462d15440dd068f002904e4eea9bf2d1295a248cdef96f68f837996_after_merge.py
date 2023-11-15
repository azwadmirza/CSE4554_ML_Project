        def _delayed_create(create_opts, dataset):
            try:
                if 'platform_name' not in kwargs:
                    kwargs['platform_name'] = dataset.attrs['platform_name']
                if 'name' not in kwargs:
                    kwargs['name'] = dataset.attrs['name']
                if 'start_time' not in kwargs:
                    kwargs['start_time'] = dataset.attrs['start_time']
                if 'sensor' not in kwargs:
                    kwargs['sensor'] = dataset.attrs['sensor']

                try:
                    self.mitiff_config[kwargs['sensor']] = dataset.attrs['metadata_requirements']['config']
                    self.channel_order[kwargs['sensor']] = dataset.attrs['metadata_requirements']['order']
                    self.file_pattern = dataset.attrs['metadata_requirements']['file_pattern']
                except KeyError:
                    # For some mitiff products this info is needed, for others not.
                    # If needed you should know how to fix this
                    pass

                try:
                    self.translate_channel_name[kwargs['sensor']] = \
                        dataset.attrs['metadata_requirements']['translate']
                except KeyError:
                    # For some mitiff products this info is needed, for others not.
                    # If needed you should know how to fix this
                    pass

                image_description = self._make_image_description(dataset, **kwargs)
                gen_filename = filename or self.get_filename(**dataset.attrs)
                LOG.info("Saving mitiff to: %s ...", gen_filename)
                self._save_datasets_as_mitiff(dataset, image_description,
                                              gen_filename, **kwargs)
            except:
                raise