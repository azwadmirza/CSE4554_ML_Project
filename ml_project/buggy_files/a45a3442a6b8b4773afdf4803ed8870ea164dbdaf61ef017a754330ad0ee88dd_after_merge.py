def _get_first_line(rfile):
    try:
        line = rfile.readline()
        if line == b"\r\n" or line == b"\n":
            # Possible leftover from previous message
            line = rfile.readline()
    except (exceptions.TcpDisconnect, exceptions.TlsException):
        raise exceptions.HttpReadDisconnect("Remote disconnected")
    if not line:
        raise exceptions.HttpReadDisconnect("Remote disconnected")
    return line.strip()