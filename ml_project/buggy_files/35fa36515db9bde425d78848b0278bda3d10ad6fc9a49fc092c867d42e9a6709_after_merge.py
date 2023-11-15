def _eventlet_sendfile(fdout, fdin, offset, nbytes, _os_sendfile=os.sendfile):
    while True:
        try:
            return _os_sendfile(fdout, fdin, offset, nbytes)
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                trampoline(fdout, write=True)
            else:
                raise