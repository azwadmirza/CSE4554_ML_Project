def init_ida_rpc_client():
    global _ida, _ida_last_exception, _ida_last_connection_check

    if not ida_enabled:
        return

    now = time.time()
    if _ida is None and (now - _ida_last_connection_check) < int(ida_timeout) + 5:
        return

    addr = 'http://{host}:{port}'.format(host=ida_rpc_host, port=ida_rpc_port)

    _ida = xmlrpclib.ServerProxy(addr)
    socket.setdefaulttimeout(int(ida_timeout))

    exception = None # (type, value, traceback)
    try:
        _ida.here()
        print(message.success("Pwndbg successfully connected to Ida Pro xmlrpc: %s" % addr))
    except socket.error as e:
        if e.errno != errno.ECONNREFUSED:
            exception = sys.exc_info()
        _ida = None
    except socket.timeout:
        exception = sys.exc_info()
        _ida = None
    except xmlrpclib.ProtocolError:
        exception = sys.exc_info()
        _ida = None

    if exception:
        if not isinstance(_ida_last_exception, exception[0]) or _ida_last_exception.args != exception[1].args:
            if hasattr(pwndbg.config, "exception_verbose") and pwndbg.config.exception_verbose:
                print(message.error("[!] Ida Pro xmlrpc error"))
                traceback.print_exception(*exception)
            else:
                exc_type, exc_value, _ = exception
                print(message.error('Failed to connect to IDA Pro ({}: {})'.format(exc_type.__qualname__, exc_value)))
                if exc_type is socket.timeout:
                    print(message.notice('To increase the time to wait for IDA Pro use `') + message.hint('set ida-timeout <new-timeout-in-seconds>') + message.notice('`'))
                else:
                    print(message.notice('For more info invoke `') + message.hint('set exception-verbose on') + message.notice('`'))
                print(message.notice('To disable IDA Pro integration invoke `') + message.hint('set ida-enabled off') + message.notice('`'))

    _ida_last_exception = exception and exception[1]
    _ida_last_connection_check = now