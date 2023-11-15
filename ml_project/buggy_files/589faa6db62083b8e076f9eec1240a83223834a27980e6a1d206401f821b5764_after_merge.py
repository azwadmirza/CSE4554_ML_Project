def dns_check(addr, port=80, safe=False, ipv6=None):
    '''
    Return the ip resolved by dns, but do not exit on failure, only raise an
    exception. Obeys system preference for IPv4/6 address resolution - this
    can be overridden by the ipv6 flag.
    Tries to connect to the address before considering it useful. If no address
    can be reached, the first one resolved is used as a fallback.
    '''
    error = False
    lookup = addr
    seen_ipv6 = False
    family = socket.AF_INET6 if ipv6 else socket.AF_INET if ipv6 is False else socket.AF_UNSPEC
    try:
        refresh_dns()
        hostnames = socket.getaddrinfo(addr, int(port), family, socket.SOCK_STREAM)
        if not hostnames:
            error = True
        else:
            resolved = False
            candidates = []
            for h in hostnames:
                # Input is IP address, passed through unchanged, just return it
                if h[4][0] == addr:
                    resolved = salt.utils.zeromq.ip_bracket(addr)
                    break

                candidate_addr = salt.utils.zeromq.ip_bracket(h[4][0])
                candidates.append(candidate_addr)

                try:
                    s = socket.socket(h[0], socket.SOCK_STREAM)
                    s.connect((candidate_addr.strip('[]'), h[4][1]))
                    s.close()

                    resolved = candidate_addr
                    break
                except socket.error:
                    pass
            if not resolved:
                if len(candidates) > 0:
                    resolved = candidates[0]
                else:
                    error = True
    except TypeError:
        err = ('Attempt to resolve address \'{0}\' failed. Invalid or unresolveable address').format(lookup)
        raise SaltSystemExit(code=42, msg=err)
    except socket.error:
        error = True

    if error:
        err = ('DNS lookup or connection check of \'{0}\' failed.').format(addr)
        if safe:
            if salt.log.is_console_configured():
                # If logging is not configured it also means that either
                # the master or minion instance calling this hasn't even
                # started running
                log.error(err)
            raise SaltClientError()
        raise SaltSystemExit(code=42, msg=err)
    return resolved