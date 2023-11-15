    def create_connection_vlan(self):
        cmd = [self.nmcli_bin]
        cmd.append('con')
        cmd.append('add')
        cmd.append('type')
        cmd.append('vlan')
        cmd.append('con-name')

        if self.conn_name is not None:
            cmd.append(self.conn_name)
        elif self.ifname is not None:
            cmd.append(self.ifname)
        else:
            cmd.append('vlan%s' % self.vlanid)

        cmd.append('ifname')
        if self.ifname is not None:
            cmd.append(self.ifname)
        elif self.conn_name is not None:
            cmd.append(self.conn_name)
        else:
            cmd.append('vlan%s' % self.vlanid)

        params = {'dev': self.vlandev,
                  'id': str(self.vlanid),
                  'ip4': self.ip4 or '',
                  'gw4': self.gw4 or '',
                  'ip6': self.ip6 or '',
                  'gw6': self.gw6 or '',
                  'autoconnect': self.bool_to_string(self.autoconnect)
                  }
        for k, v in params.items():
            cmd.extend([k, v])

        return cmd