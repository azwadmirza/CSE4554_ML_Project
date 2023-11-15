    def wrapped(self, raw):
        """
        Wraps the raw IO object (`RawIOBase` or `io.TextIOBase`) in
        buffers, text decoding, and newline handling.
        """
        # pylint:disable=too-many-branches
        result = raw
        buffering = self.buffering

        line_buffering = False
        if buffering == 1 or buffering < 0 and raw.isatty():
            buffering = -1
            line_buffering = True
        if buffering < 0:
            buffering = self.default_buffer_size
            try:
                bs = os.fstat(raw.fileno()).st_blksize
            except (OSError, AttributeError):
                pass
            else:
                if bs > 1:
                    buffering = bs
        if buffering < 0: # pragma: no cover
            raise ValueError("invalid buffering size")

        if not isinstance(raw, io.BufferedIOBase) and \
           (not hasattr(raw, 'buffer') or raw.buffer is None):
            # Need to wrap our own buffering around it. If it
            # is already buffered, don't do so.
            if buffering != 0:
                if self.updating:
                    Buffer = io.BufferedRandom
                elif self.creating or self.writing or self.appending:
                    Buffer = io.BufferedWriter
                elif self.reading:
                    Buffer = io.BufferedReader
                else: # prgama: no cover
                    raise ValueError("unknown mode: %r" % self.mode)

                try:
                    result = Buffer(raw, buffering)
                except AttributeError:
                    # Python 2 file() objects don't have the readable/writable
                    # attributes. But they handle their own buffering.
                    result = raw

        if self.binary:
            if isinstance(raw, io.TextIOBase):
                # Can't do it. The TextIO object will have its own buffer, and
                # trying to read from the raw stream or the buffer without going through
                # the TextIO object is likely to lead to problems with the codec.
                raise ValueError("Unable to perform binary IO on top of text IO stream")
            return result

        # Either native or text at this point.
        if PY2 and self.native:
            # Neither text mode nor binary mode specified.
            if self.universal:
                # universal was requested, e.g., 'rU'
                result = UniversalNewlineBytesWrapper(result, line_buffering)
        else:
            # Python 2 and text mode, or Python 3 and either text or native (both are the same)
            if not isinstance(raw, io.TextIOBase):
                # Avoid double-wrapping a TextIOBase in another TextIOWrapper.
                # That tends not to work. See https://github.com/gevent/gevent/issues/1542
                result = io.TextIOWrapper(result, self.encoding, self.errors, self.newline,
                                          line_buffering)

        if result is not raw:
            # Set the mode, if possible, but only if we created a new
            # object.
            try:
                result.mode = self.mode
            except (AttributeError, TypeError):
                # AttributeError: No such attribute
                # TypeError: Readonly attribute (py2)
                pass

        return result