    def modify_connection_vlan(self):
        cmd = [self.nmcli_bin]
        cmd.append('con')
        cmd.append('mod')

        if self.conn_name is not None:
            cmd.append(self.conn_name)
        elif self.ifname is not None:
            cmd.append(self.ifname)
        else:
            cmd.append('vlan%s' % self.vlanid)

        params = {'vlan.parent': self.vlandev,
                  'vlan.id': self.vlanid,
                  'ipv4.address': self.ip4 or '',
                  'ipv4.gateway': self.gw4 or '',
                  'ipv4.dns': self.dns4 or '',
                  'ipv6.address': self.ip6 or '',
                  'ipv6.gateway': self.gw6 or '',
                  'ipv6.dns': self.dns6 or '',
                  'autoconnect': self.bool_to_string(self.autoconnect)
                  }

        for k, v in params.items():
            cmd.extend([k, v])

        return cmd