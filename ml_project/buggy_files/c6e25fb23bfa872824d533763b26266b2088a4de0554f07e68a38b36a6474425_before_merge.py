def _gevent_sendfile(fdout, fdin, offset, nbytes):
    while True:
        try:
            return os.sendfile(fdout, fdin, offset, nbytes)
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                socket.wait_write(fdout)
            else:
                raise