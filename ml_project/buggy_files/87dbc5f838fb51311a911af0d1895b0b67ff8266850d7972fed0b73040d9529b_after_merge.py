    def down_connection(self):
        cmd = [self.nmcli_bin, 'con', 'down', self.conn_name]
        # if self.connection_exists():
        return self.execute_command(cmd)