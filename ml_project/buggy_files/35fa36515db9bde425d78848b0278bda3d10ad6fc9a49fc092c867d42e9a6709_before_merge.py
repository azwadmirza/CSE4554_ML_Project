def _eventlet_sendfile(fdout, fdin, offset, nbytes):
    while True:
        try:
            return os.sendfile(fdout, fdin, offset, nbytes)
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                trampoline(fdout, write=True)
            else:
                raise