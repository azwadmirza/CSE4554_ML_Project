    def display_results(self, endpoints, fields, sort_by=0, max_width=0, unique=False, nonzero=False):
        matrix = []
        fields_lookup = {'id': (PoseidonShell._get_name, 0),
                         'mac address': (PoseidonShell._get_mac, 1),
                         'switch': (PoseidonShell._get_switch, 2),
                         'port': (PoseidonShell._get_port, 3),
                         'vlan': (PoseidonShell._get_vlan, 4),
                         'ipv4': (PoseidonShell._get_ipv4, 5),
                         'ipv6': (PoseidonShell._get_ipv6, 6),
                         'ignored': (PoseidonShell._get_ignored, 7),
                         'state': (PoseidonShell._get_state, 8),
                         'next state': (PoseidonShell._get_next_state, 9),
                         'first seen': (PoseidonShell._get_first_seen, 10),
                         'last seen': (PoseidonShell._get_last_seen, 11),
                         'previous states': (PoseidonShell._get_prev_states, 12),
                         'ipv4 os': (PoseidonShell._get_ipv4_os, 13),
                         'ipv6 os': (PoseidonShell._get_ipv6_os, 14),
                         'previous ipv4 oses': (PoseidonShell._get_prev_ipv4_oses, 15),
                         'previous ipv6 oses': (PoseidonShell._get_prev_ipv6_oses, 16),
                         'role': (PoseidonShell._get_role, 17),
                         'role (confidence)': (PoseidonShell._get_role, 17),
                         'previous roles': (PoseidonShell._get_prev_roles, 18),
                         'behavior': (PoseidonShell._get_behavior, 19),
                         'previous behaviors': (PoseidonShell._get_prev_behaviors, 20)}
        # TODO #971 check if unqiue flag and limit columns (fields)
        # TODO #963 check if nonzero flag and limit rows/columns
        for endpoint in endpoints:
            record = []
            for field in fields:
                record.append(fields_lookup[field.lower()][0](endpoint))
            matrix.append(record)
        if len(matrix) > 0:
            matrix = sorted(matrix, key=lambda endpoint: endpoint[sort_by])
            # swap out field names for header
            fields_header = []
            for field in fields:
                fields_header.append(
                    self.all_fields[fields_lookup[field.lower()][1]])
            # set the header
            matrix.insert(0, fields_header)
            table = Texttable(max_width=max_width)
            # make all the column types be text
            table.set_cols_dtype(['t']*len(fields))
            table.add_rows(matrix)
            print(table.draw())
        else:
            print('No results found for that query.')
        return