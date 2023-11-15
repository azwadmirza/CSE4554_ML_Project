    def get_optics(self):
        """Return optics information."""
        optics_table = junos_views.junos_intf_optics_table(self.device)
        optics_table.get()
        optics_items = optics_table.items()

        # optics_items has no lane information, so we need to re-format data
        # inserting lane 0 for all optics. Note it contains all optics 10G/40G/100G
        # but the information for 40G/100G is incorrect at this point
        # Example: intf_optic item is now: ('xe-0/0/0', [ optical_values ])
        optics_items_with_lane = []
        for intf_optic_item in optics_items:
            temp_list = list(intf_optic_item)
            temp_list.insert(1, u"0")
            new_intf_optic_item = tuple(temp_list)
            optics_items_with_lane.append(new_intf_optic_item)

        # Now optics_items_with_lane has all optics with lane 0 included
        # Example: ('xe-0/0/0', u'0', [ optical_values ])

        # Get optical information for 40G/100G optics
        optics_table40G = junos_views.junos_intf_40Goptics_table(self.device)
        optics_table40G.get()
        optics_40Gitems = optics_table40G.items()

        # Re-format data as before inserting lane value
        new_optics_40Gitems = []
        for item in optics_40Gitems:
            lane = item[0]
            iface = item[1].pop(0)
            new_optics_40Gitems.append((iface[1], py23_compat.text_type(lane), item[1]))

        # New_optics_40Gitems contains 40G/100G optics only:
        # ('et-0/0/49', u'0', [ optical_values ]),
        # ('et-0/0/49', u'1', [ optical_values ]),
        # ('et-0/0/49', u'2', [ optical_values ])

        # Remove 40G/100G optics entries with wrong information returned
        # from junos_intf_optics_table()
        iface_40G = [item[0] for item in new_optics_40Gitems]
        for intf_optic_item in optics_items_with_lane:
            iface_name = intf_optic_item[0]
            if iface_name not in iface_40G:
                new_optics_40Gitems.append(intf_optic_item)

        # New_optics_40Gitems contains all optics 10G/40G/100G with the lane
        optics_detail = {}
        for intf_optic_item in new_optics_40Gitems:
            lane = intf_optic_item[1]
            interface_name = py23_compat.text_type(intf_optic_item[0])
            optics = dict(intf_optic_item[2])
            if interface_name not in optics_detail:
                optics_detail[interface_name] = {}
                optics_detail[interface_name]['physical_channels'] = {}
                optics_detail[interface_name]['physical_channels']['channel'] = []

            # Defaulting avg, min, max values to 0.0 since device does not
            # return these values
            intf_optics = {
                            'index': int(lane),
                            'state': {
                                'input_power': {
                                    'instant': (
                                        float(optics['input_power'])
                                        if optics['input_power'] not in
                                        [None, C.OPTICS_NULL_LEVEL]
                                        else 0.0),
                                    'avg': 0.0,
                                    'max': 0.0,
                                    'min': 0.0
                                    },
                                'output_power': {
                                    'instant': (
                                        float(optics['output_power'])
                                        if optics['output_power'] not in
                                        [None, C.OPTICS_NULL_LEVEL]
                                        else 0.0),
                                    'avg': 0.0,
                                    'max': 0.0,
                                    'min': 0.0
                                    },
                                'laser_bias_current': {
                                    'instant': (
                                        float(optics['laser_bias_current'])
                                        if optics['laser_bias_current'] not in
                                        [None, C.OPTICS_NULL_LEVEL]
                                        else 0.0),
                                    'avg': 0.0,
                                    'max': 0.0,
                                    'min': 0.0
                                    }
                                }
                            }
            optics_detail[interface_name]['physical_channels']['channel'].append(intf_optics)

        return optics_detail