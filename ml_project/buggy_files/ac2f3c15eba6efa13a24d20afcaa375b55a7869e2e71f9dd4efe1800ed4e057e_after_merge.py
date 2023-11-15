def _destination_and_source(af, where, port, source, source_port,
                            default_to_inet=True):
    # Apply defaults and compute destination and source tuples
    # suitable for use in connect(), sendto(), or bind().
    if af is None:
        try:
            af = dns.inet.af_for_address(where)
        except Exception:
            if default_to_inet:
                af = dns.inet.AF_INET
    if af == dns.inet.AF_INET:
        destination = (where, port)
        if source is not None or source_port != 0:
            if source is None:
                source = '0.0.0.0'
            source = (source, source_port)
    elif af == dns.inet.AF_INET6:
        ai_flags = socket.AI_NUMERICHOST
        ((*_, destination), *_) = socket.getaddrinfo(where, port,
                                                     flags=ai_flags)
        if source is not None or source_port != 0:
            if source is None:
                source = '::'
            ((*_, source), *_) = socket.getaddrinfo(source, source_port,
                                                    flags=ai_flags)
    else:
        source = None
        destination = None
    return (af, destination, source)