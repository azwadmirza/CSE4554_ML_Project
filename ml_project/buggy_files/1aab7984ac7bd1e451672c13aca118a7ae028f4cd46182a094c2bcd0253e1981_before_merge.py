    def modify_connection_bridge(self):
        cmd = [self.module.get_bin_path('nmcli', True)]
        # format for modifying bridge interface
        return cmd