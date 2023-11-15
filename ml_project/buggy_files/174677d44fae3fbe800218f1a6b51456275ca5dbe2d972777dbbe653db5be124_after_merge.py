def semanage_port_get_type(seport, port, proto):
    """ Get the SELinux type of the specified port.

    :param seport: Instance of seobject.portRecords

    :type port: str
    :param port: Port or port range (example: "8080", "8080-9090")

    :type proto: str
    :param proto: Protocol ('tcp' or 'udp')

    :rtype: tuple
    :return: Tuple containing the SELinux type and MLS/MCS level, or None if not found.
    """
    if isinstance(port, str):
        ports = port.split('-', 1)
        if len(ports) == 1:
            ports.extend(ports)
    else:
        ports = (port, port)

    key = (int(ports[0]), int(ports[1]), proto)

    records = seport.get_all()
    if key in records:
        return records[key]
    else:
        return None