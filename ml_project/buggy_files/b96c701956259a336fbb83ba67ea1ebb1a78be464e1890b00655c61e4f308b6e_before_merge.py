    def remove_connection(self):
        # self.down_connection()
        cmd = [self.module.get_bin_path('nmcli', True)]
        cmd.append('con')
        cmd.append('del')
        cmd.append(self.conn_name)
        return self.execute_command(cmd)