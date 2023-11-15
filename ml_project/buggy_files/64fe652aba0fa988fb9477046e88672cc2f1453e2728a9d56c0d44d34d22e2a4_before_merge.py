    def create_connection_team_slave(self):
        cmd = [self.module.get_bin_path('nmcli', True)]
        # format for creating team-slave interface
        cmd.append('connection')
        cmd.append('add')
        cmd.append('type')
        cmd.append(self.type)
        cmd.append('con-name')
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