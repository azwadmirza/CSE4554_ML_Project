    def get_previous_config_fpath(self):
        """
        Override method.

        Return the last configuration file used if found.
        """
        fpath = self.get_config_fpath()
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