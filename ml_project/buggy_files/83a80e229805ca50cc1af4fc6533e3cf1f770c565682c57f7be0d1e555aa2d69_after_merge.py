    def get_facts(self):
        """Return a set of facts from the devices."""
        # default values.
        vendor = u'Cisco'
        uptime = -1
        serial_number, fqdn, os_version, hostname, domain_name, model = ('',) * 6

        # obtain output from device
        show_ver = self.device.send_command('show version')
        show_hosts = self.device.send_command('show hosts')
        show_int_status = self.device.send_command('show interface status')
        show_hostname = self.device.send_command('show hostname')

        # uptime/serial_number/IOS version
        for line in show_ver.splitlines():
            if ' uptime is ' in line:
                _, uptime_str = line.split(' uptime is ')
                uptime = self.parse_uptime(uptime_str)

            if 'Processor Board ID' in line:
                _, serial_number = line.split("Processor Board ID ")
                serial_number = serial_number.strip()

            if 'system: ' in line or 'NXOS: ' in line:
                line = line.strip()
                os_version = line.split()[2]
                os_version = os_version.strip()

            if 'cisco' in line and 'hassis' in line:
                match = re.search(r'.cisco (.*) \(', line)
                if match:
                    model = match.group(1).strip()
                match = re.search(r'.cisco (.* [cC]hassis)', line)
                if match:
                    model = match.group(1).strip()

        hostname = show_hostname.strip()

        # Determine domain_name and fqdn
        for line in show_hosts.splitlines():
            if 'Default domain' in line:
                _, domain_name = re.split(r".*Default domain.*is ", line)
                domain_name = domain_name.strip()
                break
        if hostname.count(".") >= 2:
            fqdn = hostname
            # Remove domain name from hostname
            if domain_name:
                hostname = re.sub(re.escape(domain_name) + '$', '', hostname)
                hostname = hostname.strip('.')
        elif domain_name:
            fqdn = '{}.{}'.format(hostname, domain_name)

        # interface_list filter
        interface_list = []
        show_int_status = show_int_status.strip()
        # Remove the header information
        show_int_status = re.sub(r'(?:^---------+$|^Port .*$|^ .*$)', '',
                                 show_int_status, flags=re.M)
        for line in show_int_status.splitlines():
            if not line:
                continue
            interface = line.split()[0]
            # Return canonical interface name
            interface_list.append(canonical_interface_name(interface))

        return {
            'uptime': int(uptime),
            'vendor': vendor,
            'os_version': py23_compat.text_type(os_version),
            'serial_number': py23_compat.text_type(serial_number),
            'model': py23_compat.text_type(model),
            'hostname': py23_compat.text_type(hostname),
            'fqdn': fqdn,
            'interface_list': interface_list
        }