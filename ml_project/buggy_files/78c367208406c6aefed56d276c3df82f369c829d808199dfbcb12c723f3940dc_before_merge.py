    def _parse_interfaces_config(self, if_type, if_config):
        ipaddr_attr = self.IP_ADDR_ATTR_MAP[if_type]
        for if_data in if_config:
            if_name = self.get_config_attr(if_data, 'header')
            regex = self.IF_TYPE_MAP[if_type]
            match = regex.match(if_name)
            if not match:
                continue
            ipv4 = self.get_config_attr(if_data, ipaddr_attr)
            if ipv4:
                ipv4 = ipv4.replace(' ', '')
            ipv6 = self.get_config_attr(if_data, 'IPv6 address(es)')
            if ipv6:
                ipv6 = ipv6.replace('[primary]', '')
                ipv6 = ipv6.strip()
            if_id = match.group(1)
            switchport = self.get_config_attr(if_data, 'Switchport mode')
            if_obj = {
                'name': if_name,
                'if_id': if_id,
                'if_type': if_type,
                'ipv4': ipv4,
                'ipv6': ipv6,
                'switchport': switchport,
            }
            self._current_config[if_name] = if_obj