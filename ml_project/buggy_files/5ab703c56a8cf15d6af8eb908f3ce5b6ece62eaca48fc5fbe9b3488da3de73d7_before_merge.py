    def save_dataset(self, dataset, filename=None, fill_value=None,
                     compute=True, base_dir=None, **kwargs):
        LOG.debug("Starting in mitiff save_dataset ... ")

        def _delayed_create(create_opts, dataset):
            LOG.debug("create_opts: %s", create_opts)
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
                except KeyError as ke:
                    LOG.warning("Something went wrong with assigning to various dicts: %s", ke)

                try:
                    self.translate_channel_name[kwargs['sensor']] = \
                        dataset.attrs['metadata_requirements']['translate']
                except KeyError as ke:
                    LOG.warning("Something went wrong with assigning to translate: %s", ke)

                image_description = self._make_image_description(dataset, **kwargs)
                LOG.debug("File pattern %s", self.file_pattern)
                self.filename_parser = self.create_filename_parser(create_opts)
                gen_filename = filename or self.get_filename(**kwargs)
                LOG.info("Saving mitiff to: %s ...", gen_filename)
                self._save_datasets_as_mitiff(dataset, image_description,
                                              gen_filename, **kwargs)
            except:
                raise

        save_dir = "./"
        if 'mitiff_dir' in kwargs:
            save_dir = kwargs['mitiff_dir']
        elif 'base_dir' in kwargs:
            save_dir = kwargs['base_dir']
        elif base_dir:
            save_dir = base_dir
        else:
            LOG.warning("Unset save_dir. Use: %s", save_dir)
        create_opts = (save_dir)
        delayed = dask.delayed(_delayed_create)(create_opts, dataset)

        if compute:
            return delayed.compute()
        return delayed