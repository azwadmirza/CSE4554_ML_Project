def tcp(q, where, timeout=None, port=53, af=None, source=None, source_port=0,
        one_rr_per_rrset=False):
    """Return the response obtained after sending a query via TCP.

    *q*, a ``dns.message.message``, the query to send

    *where*, a ``text`` containing an IPv4 or IPv6 address,  where
    to send the message.

    *timeout*, a ``float`` or ``None``, the number of seconds to wait before the
    query times out.  If ``None``, the default, wait forever.

    *port*, an ``int``, the port send the message to.  The default is 53.

    *af*, an ``int``, the address family to use.  The default is ``None``,
    which causes the address family to use to be inferred from the form of
    *where*.  If the inference attempt fails, AF_INET is used.  This
    parameter is historical; you need never set it.

    *source*, a ``text`` containing an IPv4 or IPv6 address, specifying
    the source address.  The default is the wildcard address.

    *source_port*, an ``int``, the port from which to send the message.
    The default is 0.

    *one_rr_per_rrset*, a ``bool``.  If ``True``, put each RR into its own
    RRset.

    Returns a ``dns.message.Message``.
    """

    wire = q.to_wire()
    (af, destination, source) = _destination_and_source(af, where, port,
                                                        source, source_port)
    s = socket_factory(af, socket.SOCK_STREAM, 0)
    begin_time = None
    received_time = None
    try:
        expiration = _compute_expiration(timeout)
        s.setblocking(0)
        begin_time = time.time()
        if source is not None:
            s.bind(source)
        _connect(s, destination)
        send_tcp(s, wire, expiration)
        (r, received_time) = receive_tcp(s, expiration, one_rr_per_rrset,
                                         q.keyring, q.request_mac)
    finally:
        if begin_time is None or received_time is None:
            response_time = 0
        else:
            response_time = received_time - begin_time
        s.close()
    r.time = response_time
    if not q.is_response(r):
        raise BadResponse
    return r