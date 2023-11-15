    def get_bgp_neighbors(self):
        """BGP neighbor information.

        Supports both IPv4 and IPv6. vrf aware
        """
        supported_afi = [
            "ipv4 unicast",
            "ipv4 multicast",
            "ipv6 unicast",
            "ipv6 multicast",
            "vpnv4 unicast",
            "vpnv6 unicast",
            "ipv4 mdt",
        ]

        bgp_neighbor_data = dict()
        # vrfs where bgp is configured
        bgp_config_vrfs = []
        # get summary output from device
        cmd_bgp_all_sum = "show bgp all summary"
        summary_output = self._send_command(cmd_bgp_all_sum).strip()
        bgp_not_running = ["Invalid input", "BGP not active"]
        if any((s in summary_output for s in bgp_not_running)):
            return {}

        # get neighbor output from device
        neighbor_output = ""
        for afi in supported_afi:
            if afi in [
                "ipv4 unicast",
                "ipv4 multicast",
                "ipv6 unicast",
                "ipv6 multicast",
            ]:
                cmd_bgp_neighbor = "show bgp %s neighbors" % afi
                neighbor_output += self._send_command(cmd_bgp_neighbor).strip()
                # trailing newline required for parsing
                neighbor_output += "\n"
            elif afi in ["vpnv4 unicast", "vpnv6 unicast", "ipv4 mdt"]:
                cmd_bgp_neighbor = "show bgp %s all neighbors" % afi
                neighbor_output += self._send_command(cmd_bgp_neighbor).strip()
                # trailing newline required for parsing
                neighbor_output += "\n"

        # Regular expressions used for parsing BGP summary
        parse_summary = {
            "patterns": [
                # For address family: IPv4 Unicast
                # variable afi contains both afi and safi, i.e 'IPv4 Unicast'
                {
                    "regexp": re.compile(r"^For address family: (?P<afi>[\S ]+)$"),
                    "record": False,
                },
                # Capture router_id and local_as values, e.g.:
                # BGP router identifier 10.0.1.1, local AS number 65000
                {
                    "regexp": re.compile(
                        r"^.* router identifier (?P<router_id>{}), "
                        r"local AS number (?P<local_as>{})".format(
                            IPV4_ADDR_REGEX, ASN_REGEX
                        )
                    ),
                    "record": False,
                },
                # Match neighbor summary row, capturing useful details and
                # discarding the 5 columns that we don't care about, e.g.:
                # Neighbor   V          AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
                # 10.0.0.2   4       65000 1336020 64337701 1011343614    0    0 8w0d         3143
                {
                    "regexp": re.compile(
                        r"^\*?(?P<remote_addr>({})|({}))"
                        r"\s+\d+\s+(?P<remote_as>{})(\s+\S+){{5}}\s+"
                        r"(?P<uptime>(never)|\d+\S+)"
                        r"\s+(?P<accepted_prefixes>\d+)".format(
                            IPV4_ADDR_REGEX, IPV6_ADDR_REGEX, ASN_REGEX
                        )
                    ),
                    "record": True,
                },
                # Same as above, but for peer that are not Established, e.g.:
                # Neighbor      V       AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
                # 192.168.0.2   4    65002       0       0        1    0    0 never    Active
                {
                    "regexp": re.compile(
                        r"^\*?(?P<remote_addr>({})|({}))"
                        r"\s+\d+\s+(?P<remote_as>{})(\s+\S+){{5}}\s+"
                        r"(?P<uptime>(never)|\d+\S+)\s+(?P<state>\D.*)".format(
                            IPV4_ADDR_REGEX, IPV6_ADDR_REGEX, ASN_REGEX
                        )
                    ),
                    "record": True,
                },
                # ipv6 peers often break accross rows because of the longer peer address,
                # match as above, but in separate expressions, e.g.:
                # Neighbor      V       AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
                # 2001:DB8::4
                #               4    65004 9900690  612449 155362939    0    0 26w6d       36391
                {
                    "regexp": re.compile(
                        r"^\*?(?P<remote_addr>({})|({}))".format(
                            IPV4_ADDR_REGEX, IPV6_ADDR_REGEX
                        )
                    ),
                    "record": False,
                },
                {
                    "regexp": re.compile(
                        r"^\s+\d+\s+(?P<remote_as>{})(\s+\S+){{5}}\s+"
                        r"(?P<uptime>(never)|\d+\S+)"
                        r"\s+(?P<accepted_prefixes>\d+)".format(ASN_REGEX)
                    ),
                    "record": True,
                },
                # Same as above, but for peers that are not Established, e.g.:
                # Neighbor      V       AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
                # 2001:DB8::3
                #               4    65003       0       0        1    0    0 never    Idle (Admin)
                {
                    "regexp": re.compile(
                        r"^\s+\d+\s+(?P<remote_as>{})(\s+\S+){{5}}\s+"
                        r"(?P<uptime>(never)|\d+\S+)\s+(?P<state>\D.*)".format(
                            ASN_REGEX
                        )
                    ),
                    "record": True,
                },
            ],
            "no_fill_fields": [
                "accepted_prefixes",
                "state",
                "uptime",
                "remote_as",
                "remote_addr",
            ],
        }

        parse_neighbors = {
            "patterns": [
                # Capture BGP neighbor is 10.0.0.2,  remote AS 65000, internal link
                {
                    "regexp": re.compile(
                        r"^BGP neighbor is (?P<remote_addr>({})|({})),"
                        r"(\s+vrf (?P<vrf>\S+),)?"
                        r"\s+remote AS (?P<remote_as>{}).*".format(
                            IPV4_ADDR_REGEX, IPV6_ADDR_REGEX, ASN_REGEX
                        )
                    ),
                    "record": False,
                },
                # Capture description
                {
                    "regexp": re.compile(r"^\s+Description: (?P<description>.+)"),
                    "record": False,
                },
                # Capture remote_id, e.g.:
                # BGP version 4, remote router ID 10.0.1.2
                {
                    "regexp": re.compile(
                        r"^\s+BGP version \d+, remote router ID "
                        r"(?P<remote_id>{})".format(IPV4_ADDR_REGEX)
                    ),
                    "record": False,
                },
                # Capture state
                {
                    "regexp": re.compile(r"^\s+BGP state = (?P<state>\w+)"),
                    "record": False,
                },
                # Capture AFI and SAFI names, e.g.:
                # For address family: IPv4 Unicast
                {
                    "regexp": re.compile(r"^\s+For address family: (?P<afi>[\S ]+)$"),
                    "record": False,
                },
                # Capture current sent and accepted prefixes, e.g.:
                #     Prefixes Current:          637213       3142 (Consumes 377040 bytes)
                {
                    "regexp": re.compile(
                        r"^\s+Prefixes Current:\s+(?P<sent_prefixes>\d+)\s+"
                        r"(?P<accepted_prefixes>\d+).*"
                    ),
                    "record": False,
                },
                # Capture received_prefixes if soft-reconfig is enabled for the peer
                {
                    "regexp": re.compile(
                        r"^\s+Saved (soft-reconfig):.+(?P<received_prefixes>\d+).*"
                    ),
                    "record": True,
                },
                # Otherwise, use the following as an end of row marker
                {
                    "regexp": re.compile(r"^\s+Local Policy Denied Prefixes:.+"),
                    "record": True,
                },
            ],
            # fields that should not be "filled down" across table rows
            "no_fill_fields": [
                "received_prefixes",
                "accepted_prefixes",
                "sent_prefixes",
            ],
        }

        # Parse outputs into a list of dicts
        summary_data = []
        summary_data_entry = {}

        for line in summary_output.splitlines():
            # check for matches against each pattern
            for item in parse_summary["patterns"]:
                match = item["regexp"].match(line)
                if match:
                    # a match was found, so update the temp entry with the match's groupdict
                    summary_data_entry.update(match.groupdict())
                    if item["record"]:
                        # Record indicates the last piece of data has been obtained; move
                        # on to next entry
                        summary_data.append(copy.deepcopy(summary_data_entry))
                        # remove keys that are listed in no_fill_fields before the next pass
                        for field in parse_summary["no_fill_fields"]:
                            try:
                                del summary_data_entry[field]
                            except KeyError:
                                pass
                    break

        neighbor_data = []
        neighbor_data_entry = {}
        for line in neighbor_output.splitlines():
            # check for matches against each pattern
            for item in parse_neighbors["patterns"]:
                match = item["regexp"].match(line)
                if match:
                    # a match was found, so update the temp entry with the match's groupdict
                    neighbor_data_entry.update(match.groupdict())
                    if item["record"]:
                        # update list of vrfs where bgp is configured
                        if not neighbor_data_entry["vrf"]:
                            vrf_to_add = "global"
                        else:
                            vrf_to_add = neighbor_data_entry["vrf"]
                        if vrf_to_add not in bgp_config_vrfs:
                            bgp_config_vrfs.append(vrf_to_add)
                        # Record indicates the last piece of data has been obtained; move
                        # on to next entry
                        neighbor_data.append(copy.deepcopy(neighbor_data_entry))
                        # remove keys that are listed in no_fill_fields before the next pass
                        for field in parse_neighbors["no_fill_fields"]:
                            try:
                                del neighbor_data_entry[field]
                            except KeyError:
                                pass
                    break

        router_id = None

        for entry in summary_data:
            if not router_id:
                router_id = entry["router_id"]
            elif entry["router_id"] != router_id:
                raise ValueError

        # check the router_id looks like an ipv4 address
        router_id = napalm.base.helpers.ip(router_id, version=4)

        # create dict keys for vrfs where bgp is configured
        for vrf in bgp_config_vrfs:
            bgp_neighbor_data[vrf] = {}
            bgp_neighbor_data[vrf]["router_id"] = router_id
            bgp_neighbor_data[vrf]["peers"] = {}
        # add parsed data to output dict
        for entry in summary_data:
            remote_addr = napalm.base.helpers.ip(entry["remote_addr"])
            afi = entry["afi"].lower()
            # check that we're looking at a supported afi
            if afi not in supported_afi:
                continue
            # get neighbor_entry out of neighbor data
            neighbor_entry = None
            for neighbor in neighbor_data:
                if (
                    neighbor["afi"].lower() == afi
                    and napalm.base.helpers.ip(neighbor["remote_addr"]) == remote_addr
                ):
                    neighbor_entry = neighbor
                    break
            # check for proper session data for the afi
            if neighbor_entry is None:
                continue
            elif not isinstance(neighbor_entry, dict):
                raise ValueError(
                    msg="Couldn't find neighbor data for %s in afi %s"
                    % (remote_addr, afi)
                )

            # check for admin down state
            try:
                if "(Admin)" in entry["state"]:
                    is_enabled = False
                else:
                    is_enabled = True
            except KeyError:
                is_enabled = True

            # parse uptime value
            uptime = self.bgp_time_conversion(entry["uptime"])

            # BGP is up if state is Established
            is_up = "Established" in neighbor_entry["state"]

            # check whether session is up for address family and get prefix count
            try:
                accepted_prefixes = int(entry["accepted_prefixes"])
            except (ValueError, KeyError):
                accepted_prefixes = -1

            # Only parse neighbor detailed data if BGP session is-up
            if is_up:
                try:
                    # overide accepted_prefixes with neighbor data if possible (since that's newer)
                    accepted_prefixes = int(neighbor_entry["accepted_prefixes"])
                except (ValueError, KeyError):
                    pass

                # try to get received prefix count, otherwise set to accepted_prefixes
                received_prefixes = neighbor_entry.get(
                    "received_prefixes", accepted_prefixes
                )

                # try to get sent prefix count and convert to int, otherwise set to -1
                sent_prefixes = int(neighbor_entry.get("sent_prefixes", -1))
            else:
                received_prefixes = -1
                sent_prefixes = -1
                uptime = -1

            # get description
            try:
                description = str(neighbor_entry["description"])
            except KeyError:
                description = ""

            # check the remote router_id looks like an ipv4 address
            remote_id = napalm.base.helpers.ip(neighbor_entry["remote_id"], version=4)

            # get vrf name, if None use 'global'
            if neighbor_entry["vrf"]:
                vrf = neighbor_entry["vrf"]
            else:
                vrf = "global"

            if remote_addr not in bgp_neighbor_data[vrf]["peers"]:
                bgp_neighbor_data[vrf]["peers"][remote_addr] = {
                    "local_as": napalm.base.helpers.as_number(entry["local_as"]),
                    "remote_as": napalm.base.helpers.as_number(entry["remote_as"]),
                    "remote_id": remote_id,
                    "is_up": is_up,
                    "is_enabled": is_enabled,
                    "description": description,
                    "uptime": uptime,
                    "address_family": {
                        afi: {
                            "received_prefixes": received_prefixes,
                            "accepted_prefixes": accepted_prefixes,
                            "sent_prefixes": sent_prefixes,
                        }
                    },
                }
            else:
                # found previous data for matching remote_addr, but for different afi
                existing = bgp_neighbor_data[vrf]["peers"][remote_addr]
                assert afi not in existing["address_family"]
                # compare with existing values and croak if they don't match
                assert existing["local_as"] == napalm.base.helpers.as_number(
                    entry["local_as"]
                )
                assert existing["remote_as"] == napalm.base.helpers.as_number(
                    entry["remote_as"]
                )
                assert existing["remote_id"] == remote_id
                assert existing["is_enabled"] == is_enabled
                assert existing["description"] == description
                # merge other values in a sane manner
                existing["is_up"] = existing["is_up"] or is_up
                existing["uptime"] = max(existing["uptime"], uptime)
                existing["address_family"][afi] = {
                    "received_prefixes": received_prefixes,
                    "accepted_prefixes": accepted_prefixes,
                    "sent_prefixes": sent_prefixes,
                }
        return bgp_neighbor_data