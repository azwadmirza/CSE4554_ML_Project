    def _build_config_paths(self):
        """
        Convenience function to build up paths from our config values.  Path
        will not be relative to ``molecule_dir``, when a full path was provided
        in the config.

        :return: None
        """
        for item in ['state_file', 'vagrantfile_file', 'rakefile_file']:
            d = self.config.get('molecule')
            if d:
                d[item] = os.path.join(self.config['molecule']['molecule_dir'],
                                       self.config['molecule'][item])

        for item in ['config_file', 'inventory_file']:
            d = self.config.get('ansible')
            if d:
                d[item] = os.path.join(self.config['molecule']['molecule_dir'],
                                       self.config['ansible'][item])