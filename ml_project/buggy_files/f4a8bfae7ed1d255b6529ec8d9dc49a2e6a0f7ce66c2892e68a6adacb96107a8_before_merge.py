def init_ida_rpc_client():
    global _ida, _ida_last_exception
    addr = 'http://{host}:{port}'.format(host=ida_rpc_host, port=ida_rpc_port)

    _ida = xmlrpclib.ServerProxy(addr)
    socket.setdefaulttimeout(3)

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
            print(message.error("[!] Ida Pro xmlrpc error"))
            traceback.print_exception(*exception)

    _ida_last_exception = exception and exception[1]