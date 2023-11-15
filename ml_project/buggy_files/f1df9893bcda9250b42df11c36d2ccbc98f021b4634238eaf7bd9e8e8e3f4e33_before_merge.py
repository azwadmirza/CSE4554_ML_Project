    def get_config_fpath_from_version(self, version=None):
        """
        Override method.

        Return the configuration path for given version.

        If no version is provided, it returns the current file path.
        """
        if version is None:
            fpath = self.get_config_fpath()
        elif check_version(version, '51.0.0', '<'):
            fpath = osp.join(get_conf_path(), 'spyder.ini')
        else:
            fpath = self.get_config_fpath()

        return fpath