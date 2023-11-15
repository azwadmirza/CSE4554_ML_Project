    def display_results(self, endpoints, fields, sort_by=0, max_width=0, unique=False, nonzero=False, output_format='table', ipv4_only=True, ipv6_only=False, ipv4_and_ipv6=False):
        matrix = []
        fields_lookup = {'id': (GetData._get_name, 0),
                         'mac': (GetData._get_mac, 1),
                         'mac address': (GetData._get_mac, 1),
                         'switch': (GetData._get_switch, 2),
                         'port': (GetData._get_port, 3),
                         'vlan': (GetData._get_vlan, 4),
                         'ipv4': (GetData._get_ipv4, 5),
                         'ipv4 subnet': (GetData._get_ipv4_subnet, 6),
                         'ipv6': (GetData._get_ipv6, 7),
                         'ipv6 subnet': (GetData._get_ipv6_subnet, 8),
                         'ethernet vendor': (GetData._get_ether_vendor, 9),
                         'ignored': (GetData._get_ignored, 10),
                         'state': (GetData._get_state, 11),
                         'next state': (GetData._get_next_state, 12),
                         'first seen': (GetData._get_first_seen, 13),
                         'last seen': (GetData._get_last_seen, 14),
                         'previous states': (GetData._get_prev_states, 15),
                         'ipv4 os': (GetData._get_ipv4_os, 16),
                         'ipv4 os\n(p0f)': (GetData._get_ipv4_os, 16),
                         'ipv6 os': (GetData._get_ipv6_os, 17),
                         'ipv6 os\n(p0f)': (GetData._get_ipv6_os, 17),
                         'previous ipv4 oses': (GetData._get_prev_ipv4_oses, 18),
                         'previous ipv4 oses\n(p0f)': (GetData._get_prev_ipv4_oses, 18),
                         'previous ipv6 oses': (GetData._get_prev_ipv6_oses, 19),
                         'previous ipv6 oses\n(p0f)': (GetData._get_prev_ipv6_oses, 19),
                         'role': (GetData._get_role, 20),
                         'role\n(poseidonml)': (GetData._get_role, 20),
                         'role confidence': (GetData._get_role_confidence, 21),
                         'role confidence\n(poseidonml)': (GetData._get_role_confidence, 21),
                         'previous roles': (GetData._get_prev_roles, 22),
                         'previous roles\n(poseidonml)': (GetData._get_prev_roles, 22),
                         'previous role confidences': (GetData._get_prev_role_confidences, 23),
                         'previous role confidences\n(poseidonml)': (GetData._get_prev_role_confidences, 23),
                         'behavior': (GetData._get_behavior, 24),
                         'behavior\n(poseidonml)': (GetData._get_behavior, 24),
                         'previous behaviors': (GetData._get_prev_behaviors, 25),
                         'previous behaviors\n(poseidonml)': (GetData._get_prev_behaviors, 25),
                         'ipv4 rdns': (GetData._get_ipv4_rdns, 26),
                         'ipv6 rdns': (GetData._get_ipv6_rdns, 27),
                         'sdn controller type': (GetData._get_controller_type, 28),
                         'sdn controller uri': (GetData._get_controller, 29)}
        for index, field in enumerate(fields):
            if ipv4_only:
                if '6' in field:
                    fields[index] = field.replace('6', '4')
            if ipv6_only:
                if '4' in field:
                    fields[index] = field.replace('4', '6')
        if ipv4_and_ipv6:
            for index, field in enumerate(fields):
                if '4' in field:
                    if field.replace('4', '6') not in fields:
                        fields.insert(index + 1, field.replace('4', '6'))
                if '6' in field:
                    if field.replace('6', '4') not in fields:
                        fields.insert(index + 1, field.replace('6', '4'))

        if nonzero or unique:
            records = []
            for endpoint in endpoints:
                record = []
                for field in fields:
                    record.append(fields_lookup[field.lower()][0](endpoint))
                # remove rows that are all zero or 'NO DATA'
                if not nonzero or not all(item == '0' or item == 'NO DATA' for item in record):
                    records.append(record)

            # remove columns that are all zero or 'NO DATA'
            del_columns = []
            for i in range(len(fields)):
                marked = False
                if nonzero and all(item[i] == '0' or item[i] == 'NO DATA' for item in records):
                    del_columns.append(i)
                    marked = True
                if unique and not marked:
                    column_vals = [item[i] for item in records]
                    if len(set(column_vals)) == 1:
                        del_columns.append(i)
            del_columns.reverse()
            for val in del_columns:
                for row in records:
                    del row[val]
                del fields[val]
            if len(fields) > 0:
                matrix = records
        if not nonzero and not unique:
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