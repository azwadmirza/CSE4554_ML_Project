    def wrapped(self, raw):
        """
        Wraps the raw IO object (`RawIOBase`) in buffers, text decoding,
        and newline handling.
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
            return result
        if PY2 and self.native:
            # Neither text mode nor binary mode specified.
            if self.universal:
                # universal was requested, e.g., 'rU'
                result = UniversalNewlineBytesWrapper(result, line_buffering)
        else:
            result = io.TextIOWrapper(result, self.encoding, self.errors, self.newline,
                                      line_buffering)

        try:
            result.mode = self.mode
        except (AttributeError, TypeError):
            # AttributeError: No such attribute
            # TypeError: Readonly attribute (py2)
            pass
        return result