    def create_connection_team_slave(self):
        cmd = [self.nmcli_bin, 'connection', 'add', 'type', self.type, 'con-name']
        # format for creating team-slave interface
        if self.conn_name is not None:
            cmd.append(self.conn_name)
        elif self.ifname is not None:
            cmd.append(self.ifname)
        cmd.append('ifname')
        if self.ifname is not None:
            cmd.append(self.ifname)
        elif self.conn_name is not None:
            cmd.append(self.conn_name)
        cmd.append('master')
        if self.conn_name is not None:
            cmd.append(self.master)
        # if self.mtu is not None:
        #     cmd.append('802-3-ethernet.mtu')
        #     cmd.append(self.mtu)
        return cmd