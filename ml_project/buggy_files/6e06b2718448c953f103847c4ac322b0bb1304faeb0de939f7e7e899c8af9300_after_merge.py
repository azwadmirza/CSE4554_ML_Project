    def load_writer_config(self, config_files, **kwargs):
        """Load the writer config for *config_files*."""
        conf = {}
        for conf_fn in config_files:
            with open(conf_fn) as fd:
                conf = recursive_dict_update(conf, yaml.load(fd))
        writer_class = conf['writer']['writer']
        writer = writer_class(ppp_config_dir=self.ppp_config_dir,
                              config_files=config_files,
                              **kwargs)
        return writer