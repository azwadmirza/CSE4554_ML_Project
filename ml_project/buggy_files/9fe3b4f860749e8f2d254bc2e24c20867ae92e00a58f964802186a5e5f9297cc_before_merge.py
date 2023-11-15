def parse_host_port(host_port):
    """
    Takes a string argument specifying host or host:port.

    Returns a (hostname, port) or (ip_address, port) tuple. If no port is given,
    the second (port) element of the returned tuple will be None.

    host:port argument, for example, is accepted in the forms of:
      - hostname
      - hostname:1234
      - hostname.domain.tld
      - hostname.domain.tld:5678
      - [1234::5]:5678
      - 1234::5
      - 10.11.12.13:4567
      - 10.11.12.13
    """
    host, port = None, None  # default

    _s_ = host_port[:]
    if _s_[0] == "[":
        if "]" in host_port:
            host, _s_ = _s_.lstrip("[").rsplit("]", 1)
            host = ipaddress.IPv6Address(host).compressed
            if _s_[0] == ":":
                port = int(_s_.lstrip(":"))
            else:
                if len(_s_) > 1:
                    raise ValueError(
                        'found ambiguous "{}" port in "{}"'.format(_s_, host_port)
                    )
    else:
        if _s_.count(":") == 1:
            host, _hostport_separator_, port = _s_.partition(":")
            try:
                port = int(port)
            except ValueError as _e_:
                raise ValueError(
                    'host_port "{}" port value "{}" is not an integer.'.format(
                        host_port, port
                    )
                )
        else:
            host = _s_
    try:
        if not isinstance(host, ipaddress._BaseAddress):
            host_ip = ipaddress.ip_address(host).compressed
            host = host_ip
    except ValueError:
        log.debug('"%s" Not an IP address? Assuming it is a hostname.', host)
        if host != sanitize_host(host):
            log.error('bad hostname: "%s"', host)
            raise ValueError('bad hostname: "{}"'.format(host))

    return host, port