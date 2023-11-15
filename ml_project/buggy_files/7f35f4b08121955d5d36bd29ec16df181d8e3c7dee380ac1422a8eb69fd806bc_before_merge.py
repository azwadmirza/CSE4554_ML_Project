    def create_connection_vlan(self):
        cmd = [self.module.get_bin_path('nmcli', True)]
        # format for creating ethernet interface
        return cmd