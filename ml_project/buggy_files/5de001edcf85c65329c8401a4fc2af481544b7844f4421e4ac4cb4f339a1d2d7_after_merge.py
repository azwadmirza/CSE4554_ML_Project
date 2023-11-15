    def load(self):
        "Load image data based on tile list"

        pixel = Image.Image.load(self)

        if self.tile is None:
            raise IOError("cannot load this image")
        if not self.tile:
            return pixel

        self.map = None
        use_mmap = self.filename and len(self.tile) == 1
        # As of pypy 2.1.0, memory mapping was failing here.
        use_mmap = use_mmap and not hasattr(sys, 'pypy_version_info')

        readonly = 0

        # look for read/seek overrides
        try:
            read = self.load_read
            # don't use mmap if there are custom read/seek functions
            use_mmap = False
        except AttributeError:
            read = self.fp.read

        try:
            seek = self.load_seek
            use_mmap = False
        except AttributeError:
            seek = self.fp.seek

        if use_mmap:
            # try memory mapping
            decoder_name, extents, offset, args = self.tile[0]
            if decoder_name == "raw" and len(args) >= 3 and args[0] == self.mode \
                   and args[0] in Image._MAPMODES:
                try:
                    if hasattr(Image.core, "map"):
                        # use built-in mapper  WIN32 only
                        self.map = Image.core.map(self.filename)
                        self.map.seek(offset)
                        self.im = self.map.readimage(
                            self.mode, self.size, args[1], args[2]
                            )
                    else:
                        # use mmap, if possible
                        import mmap
                        fp = open(self.filename, "r")
                        size = os.path.getsize(self.filename)
                        self.map = mmap.mmap(fp.fileno(), size, access=mmap.ACCESS_READ)
                        self.im = Image.core.map_buffer(
                            self.map, self.size, decoder_name, extents, offset, args
                            )
                    readonly = 1
                    # After trashing self.im, we might need to reload the palette data.
                    if self.palette:
                        self.palette.dirty = 1
                except (AttributeError, EnvironmentError, ImportError):
                    self.map = None

        self.load_prepare()

        if not self.map:
            # sort tiles in file order
            self.tile.sort(key=_tilesort)

            try:
                # FIXME: This is a hack to handle TIFF's JpegTables tag.
                prefix = self.tile_prefix
            except AttributeError:
                prefix = b""

            for decoder_name, extents, offset, args in self.tile:
                decoder = Image._getdecoder(self.mode, decoder_name,
                                      args, self.decoderconfig)
                seek(offset)
                try:
                    decoder.setimage(self.im, extents)
                except ValueError:
                    continue
                if decoder.pulls_fd:
                    decoder.setfd(self.fp)
                    status, err_code = decoder.decode(b"")
                else:
                    b = prefix
                    while True:
                        try:
                            s = read(self.decodermaxblock)
                        except (IndexError, struct.error):  # truncated png/gif
                            if LOAD_TRUNCATED_IMAGES:
                                break
                            else:
                                raise IOError("image file is truncated")

                        if not s and not decoder.handles_eof:  # truncated jpeg
                            self.tile = []

                            # JpegDecode needs to clean things up here either way
                            # If we don't destroy the decompressor,
                            # we have a memory leak.
                            decoder.cleanup()

                            if LOAD_TRUNCATED_IMAGES:
                                break
                            else:
                                raise IOError("image file is truncated "
                                              "(%d bytes not processed)" % len(b))

                        b = b + s
                        n, err_code = decoder.decode(b)
                        if n < 0:
                            break
                        b = b[n:]

                # Need to cleanup here to prevent leaks in PyPy
                decoder.cleanup()

        self.tile = []
        self.readonly = readonly

        self.fp = None  # might be shared

        if not self.map and not LOAD_TRUNCATED_IMAGES and err_code < 0:
            # still raised if decoder fails to return anything
            raise_ioerror(err_code)

        # post processing
        if hasattr(self, "tile_post_rotate"):
            # FIXME: This is a hack to handle rotated PCD's
            self.im = self.im.rotate(self.tile_post_rotate)
            self.size = self.im.size

        self.load_end()

        return Image.Image.load(self)