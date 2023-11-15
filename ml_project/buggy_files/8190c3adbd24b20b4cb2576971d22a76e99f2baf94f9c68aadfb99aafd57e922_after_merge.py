    def create_connection_bridge(self):
        # format for creating bridge interface
        # To add an Bridge connection with static IP configuration, issue a command as follows
        # - nmcli: name=add conn_name=my-eth1 ifname=eth1 type=bridge ip4=192.0.2.100/24 gw4=192.0.2.1 state=present
        # nmcli con add con-name my-eth1 ifname eth1 type bridge ip4 192.0.2.100/24 gw4 192.0.2.1
        cmd = [self.nmcli_bin, 'con', 'add', 'type', 'bridge', 'con-name']
        if self.conn_name is not None:
            cmd.append(self.conn_name)
        elif self.ifname is not None:
            cmd.append(self.ifname)
        cmd.append('ifname')
        if self.ifname is not None:
            cmd.append(self.ifname)
        elif self.conn_name is not None:
            cmd.append(self.conn_name)

        options = {
            'ip4': self.ip4,
            'gw4': self.gw4,
            'ip6': self.ip6,
            'gw6': self.gw6,
            'autoconnect': self.bool_to_string(self.autoconnect),
            'bridge.ageing-time': self.ageingtime,
            'bridge.forward-delay': self.forwarddelay,
            'bridge.hello-time': self.hellotime,
            'bridge.mac-address': self.mac,
            'bridge.max-age': self.maxage,
            'bridge.priority': self.priority,
            'bridge.stp': self.bool_to_string(self.stp)
        }

        for key, value in options.items():
            if value is not None:
                cmd.extend([key, value])

        return cmd