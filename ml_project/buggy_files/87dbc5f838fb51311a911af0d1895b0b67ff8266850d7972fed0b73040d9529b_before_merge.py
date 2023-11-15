    def down_connection(self):
        cmd = [self.module.get_bin_path('nmcli', True)]
        # if self.connection_exists():
        cmd.append('con')
        cmd.append('down')
        cmd.append(self.conn_name)
        return self.execute_command(cmd)