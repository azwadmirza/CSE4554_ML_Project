    def get_interfaces_counters(self):
        """
        Return interface counters and errors.

        'tx_errors': int,
        'rx_errors': int,
        'tx_discards': int,
        'rx_discards': int,
        'tx_octets': int,
        'rx_octets': int,
        'tx_unicast_packets': int,
        'rx_unicast_packets': int,
        'tx_multicast_packets': int,
        'rx_multicast_packets': int,
        'tx_broadcast_packets': int,
        'rx_broadcast_packets': int,

        Currently doesn't determine output broadcasts, multicasts
        """
        counters = {}
        command = "show interfaces"
        output = self._send_command(command)
        sh_int_sum_cmd = "show interface summary"
        sh_int_sum_cmd_out = self._send_command(sh_int_sum_cmd)

        # Break output into per-interface sections
        interface_strings = re.split(r".* line protocol is .*", output, flags=re.M)
        header_strings = re.findall(r".* line protocol is .*", output, flags=re.M)

        empty = interface_strings.pop(0).strip()
        if empty:
            raise ValueError("Unexpected output from: {}".format(command))

        # Parse out the interface names
        intf = []
        for intf_line in header_strings:
            interface, _ = re.split(r" is .* line protocol is ", intf_line)
            intf.append(interface.strip())

        if len(intf) != len(interface_strings):
            raise ValueError("Unexpected output from: {}".format(command))

        # Re-join interface names with interface strings
        for interface, interface_str in zip(intf, interface_strings):
            counters.setdefault(interface, {})
            for line in interface_str.splitlines():
                if "packets input" in line:
                    # '0 packets input, 0 bytes, 0 no buffer'
                    match = re.search(r"(\d+) packets input.* (\d+) bytes", line)
                    counters[interface]["rx_unicast_packets"] = int(match.group(1))
                    counters[interface]["rx_octets"] = int(match.group(2))
                elif "broadcast" in line:
                    # 'Received 0 broadcasts (0 multicasts)'
                    # 'Received 264071 broadcasts (39327 IP multicasts)'
                    # 'Received 338 broadcasts, 0 runts, 0 giants, 0 throttles'
                    match = re.search(
                        r"Received (\d+) broadcasts.*(\d+).*multicasts", line
                    )
                    alt_match = re.search(r"Received (\d+) broadcasts.*", line)
                    if match:
                        counters[interface]["rx_broadcast_packets"] = int(
                            match.group(1)
                        )
                        counters[interface]["rx_multicast_packets"] = int(
                            match.group(2)
                        )
                    elif alt_match:
                        counters[interface]["rx_broadcast_packets"] = int(
                            alt_match.group(1)
                        )
                        counters[interface]["rx_multicast_packets"] = -1
                    else:
                        counters[interface]["rx_broadcast_packets"] = -1
                        counters[interface]["rx_multicast_packets"] = -1
                elif "packets output" in line:
                    # '0 packets output, 0 bytes, 0 underruns'
                    match = re.search(r"(\d+) packets output.* (\d+) bytes", line)
                    counters[interface]["tx_unicast_packets"] = int(match.group(1))
                    counters[interface]["tx_octets"] = int(match.group(2))
                    counters[interface]["tx_broadcast_packets"] = -1
                    counters[interface]["tx_multicast_packets"] = -1
                elif "input errors" in line:
                    # '0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored'
                    match = re.search(r"(\d+) input errors", line)
                    counters[interface]["rx_errors"] = int(match.group(1))
                    counters[interface]["rx_discards"] = -1
                elif "output errors" in line:
                    # '0 output errors, 0 collisions, 1 interface resets'
                    match = re.search(r"(\d+) output errors", line)
                    counters[interface]["tx_errors"] = int(match.group(1))
                    counters[interface]["tx_discards"] = -1

            interface_type, interface_number = split_interface(interface)
            if interface_type in [
                "HundredGigabitEthernet",
                "FortyGigabitEthernet",
                "TenGigabitEthernet",
            ]:
                interface = abbreviated_interface_name(interface)
            for line in sh_int_sum_cmd_out.splitlines():
                if interface in line:
                    # Line is tabular output with columns
                    # Interface  IHQ  IQD  OHQ  OQD  RXBS  RXPS  TXBS  TXPS  TRTL
                    # where columns (excluding interface) are integers
                    regex = (
                        r"\b"
                        + interface
                        + r"\b\s+(\d+)\s+(?P<IQD>\d+)\s+(\d+)"
                        + r"\s+(?P<OQD>\d+)\s+(\d+)\s+(\d+)"
                        + r"\s+(\d+)\s+(\d+)\s+(\d+)"
                    )
                    match = re.search(regex, line)
                    if match:
                        interface = canonical_interface_name(interface)
                        counters[interface]["rx_discards"] = int(match.group("IQD"))
                        counters[interface]["tx_discards"] = int(match.group("OQD"))

        return counters