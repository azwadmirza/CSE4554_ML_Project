def fromfd(fd, keep_fd=True):
    """Create a socket from a file descriptor

    socket domain (family), type and protocol are auto-detected. By default
    the socket uses a dup()ed fd. The original fd can be closed.

    The parameter `keep_fd` influences fd duplication. Under Python 2 the
    fd is still duplicated but the input fd is closed. Under Python 3 and
    with `keep_fd=True`, the new socket object uses the same fd.

    :param fd: socket fd
    :type fd: int
    :param keep_fd: keep input fd
    :type keep_fd: bool
    :return: socket.socket instance
    :raises OSError: for invalid socket fd
    """
    family = _raw_getsockname(fd)
    if hasattr(socket, 'SO_TYPE'):
        typ = _raw_getsockopt(fd, socket.SOL_SOCKET, getattr(socket, 'SO_TYPE'))
    else:
        typ = socket.SOCK_STREAM
    if hasattr(socket, 'SO_PROTOCOL'):
        proto = _raw_getsockopt(fd, socket.SOL_SOCKET, getattr(socket, 'SO_PROTOCOL'))
    else:
        proto = 0
    if keep_fd:
        return socket.fromfd(fd, family, typ, proto)
    else:
        return socket.socket(family, typ, proto, fileno=fd)