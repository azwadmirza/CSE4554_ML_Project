    def get_interfaces_ip(self):
        """
        Get interface IP details. Returns a dictionary of dictionaries.

        Sample output:
        {
            "Ethernet2/3": {
                "ipv4": {
                    "4.4.4.4": {
                        "prefix_length": 16
                    }
                },
                "ipv6": {
                    "2001:db8::1": {
                        "prefix_length": 10
                    },
                    "fe80::2ec2:60ff:fe4f:feb2": {
                        "prefix_length": "128"
                    }
                }
            },
            "Ethernet2/2": {
                "ipv4": {
                    "2.2.2.2": {
                        "prefix_length": 27
                    }
                }
            }
        }
        """
        interfaces_ip = {}
        ipv4_command = "show ip interface vrf all"
        ipv6_command = "show ipv6 interface vrf all"
        output_v4 = self._send_command(ipv4_command)
        output_v6 = self._send_command(ipv6_command)

        v4_interfaces = {}
        for line in output_v4.splitlines():
            # Ethernet2/2, Interface status: protocol-up/link-up/admin-up, iod: 38,
            # IP address: 2.2.2.2, IP subnet: 2.2.2.0/27 route-preference: 0, tag: 0
            # IP address: 3.3.3.3, IP subnet: 3.3.3.0/25 secondary route-preference: 0, tag: 0
            if "Interface status" in line:
                interface = line.split(",")[0]
                continue
            if "IP address" in line:
                ip_address = line.split(",")[0].split()[2]
                try:
                    prefix_len = int(line.split()[5].split("/")[1])
                except (ValueError, IndexError):
                    prefix_len = "N/A"

                if ip_address == "none":
                    v4_interfaces.setdefault(interface, {})
                else:
                    val = {"prefix_length": prefix_len}
                    v4_interfaces.setdefault(interface, {})[ip_address] = val

        v6_interfaces = {}
        for line in output_v6.splitlines():
            # Ethernet2/4, Interface status: protocol-up/link-up/admin-up, iod: 40
            # IPv6 address:
            #   2001:11:2233::a1/24 [VALID]
            #   2001:cc11:22bb:0:2ec2:60ff:fe4f:feb2/64 [VALID]
            # IPv6 subnet:  2001::/24
            # IPv6 link-local address: fe80::2ec2:60ff:fe4f:feb2 (default) [VALID]
            # IPv6 address: fe80::a293:51ff:fe5f:5ce9 [VALID]
            if "Interface status" in line:
                interface = line.split(",")[0]
                continue
            if "VALID" in line:
                line = line.strip()
                if "link-local address" in line:
                    # match the following format:
                    # IPv6 link-local address: fe80::2ec2:60ff:fe4f:feb2 (default) [VALID]
                    ip_address = line.split()[3]
                    prefix_len = "64"
                elif "IPv6 address" in line:
                    # match the following format:
                    # IPv6 address: fe80::a293:51ff:fe5f:5ce9 [VALID]
                    ip_address = line.split()[2]
                    prefix_len = "64"
                else:
                    ip_address, prefix_len = line.split()[0].split("/")
                prefix_len = int(prefix_len)
                val = {"prefix_length": prefix_len}
                v6_interfaces.setdefault(interface, {})[ip_address] = val
            else:
                # match the following format:
                # IPv6 address: none
                v6_interfaces.setdefault(interface, {})

        # Join data from intermediate dictionaries.
        for interface, data in v4_interfaces.items():
            interfaces_ip.setdefault(interface, {"ipv4": {}})["ipv4"] = data

        for interface, data in v6_interfaces.items():
            interfaces_ip.setdefault(interface, {"ipv6": {}})["ipv6"] = data

        return interfaces_ip