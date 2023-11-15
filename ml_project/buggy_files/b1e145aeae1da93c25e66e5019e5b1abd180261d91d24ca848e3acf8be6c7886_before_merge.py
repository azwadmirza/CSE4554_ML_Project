def parse_intf_section(interface):
    """Parse a single entry from show interfaces output.

    Different cases:
    mgmt0 is up
    admin state is up

    Ethernet2/1 is up
    admin state is up, Dedicated Interface

    Vlan1 is down (Administratively down), line protocol is down, autostate enabled

    Ethernet154/1/48 is up (with no 'admin state')
    """
    interface = interface.strip()
    re_protocol = r"^(?P<intf_name>\S+?)\s+is\s+(?P<status>.+?)" \
                  r",\s+line\s+protocol\s+is\s+(?P<protocol>\S+).*$"
    re_intf_name_state = r"^(?P<intf_name>\S+) is (?P<intf_state>\S+).*"
    re_is_enabled_1 = r"^admin state is (?P<is_enabled>\S+)$"
    re_is_enabled_2 = r"^admin state is (?P<is_enabled>\S+), "
    re_is_enabled_3 = r"^.* is down.*Administratively down.*$"
    re_mac = r"^\s+Hardware:\s+(?P<hardware>.*),\s+address:\s+(?P<mac_address>\S+) "
    re_speed = r"\s+MTU .*,\s+BW\s+(?P<speed>\S+)\s+(?P<speed_unit>\S+), "
    re_description_1 = r"^\s+Description:\s+(?P<description>.*)  (?:MTU|Internet)"
    re_description_2 = r"^\s+Description:\s+(?P<description>.*)$"
    re_hardware = r"^.* Hardware: (?P<hardware>\S+)$"

    # Check for 'protocol is ' lines
    match = re.search(re_protocol, interface, flags=re.M)
    if match:
        intf_name = match.group('intf_name')
        status = match.group('status')
        protocol = match.group('protocol')

        if 'admin' in status.lower():
            is_enabled = False
        else:
            is_enabled = True
        is_up = bool('up' in protocol)

    else:
        # More standard is up, next line admin state is lines
        match = re.search(re_intf_name_state, interface)
        intf_name = match.group('intf_name')
        intf_state = match.group('intf_state').strip()
        is_up = True if intf_state == 'up' else False

        admin_state_present = re.search("admin state is", interface)
        if admin_state_present:
            # Parse cases where 'admin state' string exists
            for x_pattern in [re_is_enabled_1, re_is_enabled_2]:
                match = re.search(x_pattern, interface, flags=re.M)
                if match:
                    is_enabled = match.group('is_enabled').strip()
                    is_enabled = True if re.search("up", is_enabled) else False
                    break
            else:
                msg = "Error parsing intf, 'admin state' never detected:\n\n{}".format(interface)
                raise ValueError(msg)
        else:
            # No 'admin state' should be 'is up' or 'is down' strings
            # If interface is up; it is enabled
            is_enabled = True
            if not is_up:
                match = re.search(re_is_enabled_3, interface, flags=re.M)
                if match:
                    is_enabled = False

    match = re.search(re_mac, interface, flags=re.M)
    if match:
        mac_address = match.group('mac_address')
        mac_address = napalm.base.helpers.mac(mac_address)
    else:
        mac_address = ""

    match = re.search(re_hardware, interface, flags=re.M)
    speed_exist = True
    if match:
        if match.group('hardware') == "NVE":
            speed_exist = False

    if speed_exist:
        match = re.search(re_speed, interface, flags=re.M)
        speed = int(match.group('speed'))
        speed_unit = match.group('speed_unit')
        # This was alway in Kbit (in the data I saw)
        if speed_unit != "Kbit":
            msg = "Unexpected speed unit in show interfaces parsing:\n\n{}".format(interface)
            raise ValueError(msg)
        speed = int(round(speed / 1000.0))
    else:
        speed = -1

    description = ''
    for x_pattern in [re_description_1, re_description_2]:
        match = re.search(x_pattern, interface, flags=re.M)
        if match:
            description = match.group('description')
            break

    return {
             intf_name: {
                    'description': description,
                    'is_enabled': is_enabled,
                    'is_up': is_up,
                    'last_flapped': -1.0,
                    'mac_address': mac_address,
                    'speed': speed}
           }