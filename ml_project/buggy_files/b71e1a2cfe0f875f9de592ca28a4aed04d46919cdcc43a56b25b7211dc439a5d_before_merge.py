    def create_connection_bridge(self):
        cmd = [self.module.get_bin_path('nmcli', True)]
        # format for creating bridge interface
        return cmd