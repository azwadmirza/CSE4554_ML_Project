    def _load_libtiff(self):
        """ Overload method triggered when we detect a compressed tiff
            Calls out to libtiff """

        pixel = Image.Image.load(self)

        if self.tile is None:
            raise IOError("cannot load this image")
        if not self.tile:
            return pixel

        self.load_prepare()

        if not len(self.tile) == 1:
            raise IOError("Not exactly one tile")

        # (self._compression, (extents tuple),
        #   0, (rawmode, self._compression, fp))
        extents = self.tile[0][1]
        args = list(self.tile[0][3])

        # To be nice on memory footprint, if there's a
        # file descriptor, use that instead of reading
        # into a string in python.
        # libtiff closes the file descriptor, so pass in a dup.
        try:
            fp = hasattr(self.fp, "fileno") and os.dup(self.fp.fileno())
            # flush the file descriptor, prevents error on pypy 2.4+
            # should also eliminate the need for fp.tell for py3
            # in _seek
            if hasattr(self.fp, "flush"):
                self.fp.flush()
        except IOError:
            # io.BytesIO have a fileno, but returns an IOError if
            # it doesn't use a file descriptor.
            fp = False

        if fp:
            args[2] = fp

        decoder = Image._getdecoder(
            self.mode, "libtiff", tuple(args), self.decoderconfig
        )
        try:
            decoder.setimage(self.im, extents)
        except ValueError:
            raise IOError("Couldn't set the image")

        if hasattr(self.fp, "getvalue"):
            # We've got a stringio like thing passed in. Yay for all in memory.
            # The decoder needs the entire file in one shot, so there's not
            # a lot we can do here other than give it the entire file.
            # unless we could do something like get the address of the
            # underlying string for stringio.
            #
            # Rearranging for supporting byteio items, since they have a fileno
            # that returns an IOError if there's no underlying fp. Easier to
            # deal with here by reordering.
            if DEBUG:
                print("have getvalue. just sending in a string from getvalue")
            n, err = decoder.decode(self.fp.getvalue())
        elif hasattr(self.fp, "fileno"):
            # we've got a actual file on disk, pass in the fp.
            if DEBUG:
                print("have fileno, calling fileno version of the decoder.")
            self.fp.seek(0)
            # 4 bytes, otherwise the trace might error out
            n, err = decoder.decode(b"fpfp")
        else:
            # we have something else.
            if DEBUG:
                print("don't have fileno or getvalue. just reading")
            # UNDONE -- so much for that buffer size thing.
            n, err = decoder.decode(self.fp.read())

        self.tile = []
        self.readonly = 0
        # libtiff closed the fp in a, we need to close self.fp, if possible
        if self._exclusive_fp and not self._is_animated:
            self.fp.close()
            self.fp = None  # might be shared

        if err < 0:
            raise IOError(err)

        return Image.Image.load(self)