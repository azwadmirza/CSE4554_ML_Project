    def save_datasets(self, datasets, compute=True, **kwargs):
        """Save all datasets to one or more files.
        """
        LOG.debug("Starting in mitiff save_datasets ... ")
        LOG.debug("kwargs: %s", kwargs)

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
                    LOG.warning("metadata requirements not given. This is ok for predefined composites in satpy")

                image_description = self._make_image_description(datasets, **kwargs)
                LOG.debug("File pattern %s", self.file_pattern)
                if isinstance(datasets, list):
                    kwargs['start_time'] = datasets[0].attrs['start_time']
                else:
                    kwargs['start_time'] = datasets.attrs['start_time']
                self.filename_parser = \
                    self.create_filename_parser(kwargs['mitiff_dir'])
                LOG.info("Saving mitiff to: %s ...", self.get_filename(**kwargs))
                gen_filename = self.get_filename(**kwargs)
                self._save_datasets_as_mitiff(datasets, image_description, gen_filename, **kwargs)
            except:
                raise

        create_opts = ()
        delayed = dask.delayed(_delayed_create)(create_opts, datasets)
        LOG.debug("About to call delayed compute ...")
        if compute:
            return delayed.compute()
        return delayed