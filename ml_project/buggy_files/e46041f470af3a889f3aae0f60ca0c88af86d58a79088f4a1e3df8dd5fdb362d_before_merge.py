    def get_mac_address_table(self):
        """
        Returns a lists of dictionaries. Each dictionary represents an entry in the MAC Address
        Table, having the following keys
            * mac (string)
            * interface (string)
            * vlan (int)
            * active (boolean)
            * static (boolean)
            * moves (int)
            * last_move (float)
        Format1:

        Legend:
        * - primary entry, G - Gateway MAC, (R) - Routed MAC, O - Overlay MAC
        age - seconds since last seen,+ - primary entry using vPC Peer-Link,
        (T) - True, (F) - False
           VLAN     MAC Address      Type      age     Secure NTFY Ports/SWID.SSID.LID
        ---------+-----------------+--------+---------+------+----+------------------
        * 27       0026.f064.0000    dynamic      -       F    F    po1
        * 27       001b.54c2.2644    dynamic      -       F    F    po1
        * 27       0000.0c9f.f2bc    dynamic      -       F    F    po1
        * 27       0026.980a.df44    dynamic      -       F    F    po1
        * 16       0050.56bb.0164    dynamic      -       F    F    po2
        * 13       90e2.ba5a.9f30    dynamic      -       F    F    eth1/2
        * 13       90e2.ba4b.fc78    dynamic      -       F    F    eth1/1
          39       0100.5e00.4b4b    igmp         0       F    F    Po1 Po2 Po22
          110      0100.5e00.0118    igmp         0       F    F    Po1 Po2
                                                                    Eth142/1/3 Eth112/1/5
                                                                    Eth112/1/6 Eth122/1/5

        """

        #  The '*' is stripped out later
        RE_MACTABLE_FORMAT1 = r"^\s+{}\s+{}\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+".format(VLAN_REGEX,
                                                                                  MAC_REGEX)
        RE_MACTABLE_FORMAT2 = r"^\s+{}\s+{}\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+".format('-',
                                                                                  MAC_REGEX)
        # REGEX dedicated for lines with only interfaces (suite of the previous MAC address)
        RE_MACTABLE_FORMAT3 = r"^\s+\S+"

        mac_address_table = []
        command = 'show mac address-table'
        output = self.device.send_command(command) # noqa

        def remove_prefix(s, prefix):
            return s[len(prefix):] if s.startswith(prefix) else s

        def process_mac_fields(vlan, mac, mac_type, interface):
            """Return proper data for mac address fields."""
            if mac_type.lower() in ['self', 'static', 'system']:
                static = True
                if vlan.lower() == 'all':
                    vlan = 0
                elif vlan == '-':
                    vlan = 0
                if interface.lower() == 'cpu' or re.search(r'router', interface.lower()) or \
                        re.search(r'switch', interface.lower()):
                    interface = ''
            else:
                static = False
            if mac_type.lower() in ['dynamic']:
                active = True
            else:
                active = False
            return {
                'mac': napalm.base.helpers.mac(mac),
                'interface': interface,
                'vlan': int(vlan),
                'static': static,
                'active': active,
                'moves': -1,
                'last_move': -1.0
            }

        # Skip the header lines
        output = re.split(r'^----.*', output, flags=re.M)[1:]
        output = "\n".join(output).strip()
        # Strip any leading characters
        output = re.sub(r"^[\*\+GO]", "", output, flags=re.M)
        output = re.sub(r"^\(R\)", "", output, flags=re.M)
        output = re.sub(r"^\(T\)", "", output, flags=re.M)
        output = re.sub(r"^\(F\)", "", output, flags=re.M)
        output = re.sub(r"vPC Peer-Link", "vPC-Peer-Link", output, flags=re.M)

        for line in output.splitlines():

            # Every 500 Mac's Legend is reprinted, regardless of terminal length
            if re.search(r'^Legend', line):
                continue
            elif re.search(r'^\s+\* \- primary entry', line):
                continue
            elif re.search(r'^\s+age \-', line):
                continue
            elif re.search(r'^\s+VLAN', line):
                continue
            elif re.search(r'^------', line):
                continue
            elif re.search(r'^\s*$', line):
                continue

            for pattern in [RE_MACTABLE_FORMAT1, RE_MACTABLE_FORMAT2, RE_MACTABLE_FORMAT3]:
                if re.search(pattern, line):
                    fields = line.split()
                    if len(fields) >= 7:
                        vlan, mac, mac_type, _, _, _, interface = fields[:7]
                        mac_address_table.append(process_mac_fields(vlan, mac, mac_type,
                                                                    interface))

                        # there can be multiples interfaces for the same MAC on the same line
                        for interface in fields[7:]:
                            mac_address_table.append(process_mac_fields(vlan, mac, mac_type,
                                                                        interface))
                        break

                    # interfaces can overhang to the next line (line only contains interfaces)
                    elif len(fields) < 7:
                        for interface in fields:
                            mac_address_table.append(process_mac_fields(vlan, mac, mac_type,
                                                                        interface))
                        break
            else:
                raise ValueError("Unexpected output from: {}".format(repr(line)))

        return mac_address_table