    def get_previous_config_fpath(self):
        """
        Override method.

        Return the last configuration file used if found.
        """
        fpath = self.get_config_fpath()

        # We don't need to add the contents of the old spyder.ini to
        # the configuration of external plugins. This was the cause
        # of  part two (the shortcut conflicts) of issue
        # spyder-ide/spyder#11132
        if self._external_plugin:
            previous_paths = [fpath]
        else:
            previous_paths = [
                # >= 51.0.0
                fpath,
                # < 51.0.0
                os.path.join(get_conf_path(), 'spyder.ini'),
            ]

        for fpath in previous_paths:
            if osp.isfile(fpath):
                break

        return fpath