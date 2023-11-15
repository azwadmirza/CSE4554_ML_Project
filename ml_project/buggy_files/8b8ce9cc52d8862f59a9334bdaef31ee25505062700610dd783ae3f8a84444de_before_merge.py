    def _redirect(self, to_fd, unbuffered=False, close=False):
        if close:
            fp = getattr(sys, self._stream)
            # TODO(jhr): does this still work under windows?  are we leaking a fd?
            # Do not close old filedescriptor as others might be using it
            fp.close()
        os.dup2(to_fd, self._old_fd)
        if self._io_wrapped:
            if close:
                setattr(sys, self._stream, getattr(sys, self._stream).output_streams[0])
            else:
                setattr(sys, self._stream, StreamFork([getattr(sys, self._stream),
                                                      os.fdopen(self._old_fd, "w")],
                                                      unbuffered=unbuffered))
        else:
            setattr(sys, self._stream, os.fdopen(self._old_fd, "w"))
            if unbuffered:
                setattr(sys, self._stream, Unbuffered(getattr(sys, self._stream)))