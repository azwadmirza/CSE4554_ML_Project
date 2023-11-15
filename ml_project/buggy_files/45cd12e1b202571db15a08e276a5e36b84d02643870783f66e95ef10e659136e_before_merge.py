    def get_lldp_neighbors(self):
        """IOS implementation of get_lldp_neighbors."""
        lldp = {}
        command = 'show lldp neighbors'
        output = self._send_command(command)

        # Check if router supports the command
        if '% Invalid input' in output:
            return {}

        # Process the output to obtain just the LLDP entries
        try:
            split_output = re.split(r'^Device ID.*$', output, flags=re.M)[1]
            split_output = re.split(r'^Total entries displayed.*$', split_output, flags=re.M)[0]
        except IndexError:
            return {}

        split_output = split_output.strip()

        for lldp_entry in split_output.splitlines():
            # Example, twb-sf-hpsw1    Fa4   120   B   17
            try:
                device_id, local_int_brief, hold_time, capability, remote_port = lldp_entry.split()
            except ValueError:
                if len(lldp_entry.split()) == 4:
                    # Four fields might be long_name or missing capability
                    capability_missing = True if lldp_entry[46] == ' ' else False
                    if capability_missing:
                        device_id, local_int_brief, hold_time, remote_port = lldp_entry.split()
                    else:
                        # Might be long_name issue
                        tmp_field, hold_time, capability, remote_port = lldp_entry.split()
                        device_id = tmp_field[:20]
                        local_int_brief = tmp_field[20:]
                        # device_id might be abbreviated, try to get full name
                        lldp_tmp = self._lldp_detail_parser(local_int_brief)
                        device_id_new = lldp_tmp[3][0]
                        # Verify abbreviated and full name are consistent
                        if device_id_new[:20] == device_id:
                            device_id = device_id_new
                        else:
                            raise ValueError("Unable to obtain remote device name")
            local_port = self._expand_interface_name(local_int_brief)

            entry = {'port': remote_port, 'hostname': device_id}
            lldp.setdefault(local_port, [])
            lldp[local_port].append(entry)

        return lldp