    def _build_config_paths(self):
        """
        Convenience function to build up paths from our config values.  Path
        will not be relative to ``molecule_dir``, when a full path was provided
        in the config.

        :return: None
        """
        md = self.config.get('molecule')
        ad = self.config.get('ansible')
        for item in ['state_file', 'vagrantfile_file', 'rakefile_file']:
            if md and not self._is_path(md[item]):
                md[item] = os.path.join(md['molecule_dir'], md[item])

        for item in ['config_file', 'inventory_file']:
            if ad and not self._is_path(ad[item]):
                ad[item] = os.path.join(md['molecule_dir'], ad[item])