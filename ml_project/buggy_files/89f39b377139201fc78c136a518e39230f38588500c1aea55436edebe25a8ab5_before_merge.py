    def _open(self):

        if self.fp.read(8) != _MAGIC:
            raise SyntaxError("not a PNG file")
        self.__fp = self.fp
        self.__frame = 0

        #
        # Parse headers up to the first IDAT or fDAT chunk

        self.png = PngStream(self.fp)

        while True:

            #
            # get next chunk

            cid, pos, length = self.png.read()

            try:
                s = self.png.call(cid, pos, length)
            except EOFError:
                break
            except AttributeError:
                logger.debug("%r %s %s (unknown)", cid, pos, length)
                s = ImageFile._safe_read(self.fp, length)

            self.png.crc(cid, s)

        #
        # Copy relevant attributes from the PngStream.  An alternative
        # would be to let the PngStream class modify these attributes
        # directly, but that introduces circular references which are
        # difficult to break if things go wrong in the decoder...
        # (believe me, I've tried ;-)

        self.mode = self.png.im_mode
        self._size = self.png.im_size
        self.info = self.png.im_info
        self._text = None
        self.tile = self.png.im_tile
        self.custom_mimetype = self.png.im_custom_mimetype
        self._n_frames = self.png.im_n_frames
        self.default_image = self.info.get("default_image", False)

        if self.png.im_palette:
            rawmode, data = self.png.im_palette
            self.palette = ImagePalette.raw(rawmode, data)

        if cid == b"fdAT":
            self.__prepare_idat = length - 4
        else:
            self.__prepare_idat = length  # used by load_prepare()

        if self._n_frames is not None:
            self._close_exclusive_fp_after_loading = False
            self.png.save_rewind()
            self.__rewind_idat = self.__prepare_idat
            self.__rewind = self.__fp.tell()
            if self.default_image:
                # IDAT chunk contains default image and not first animation frame
                self._n_frames += 1
            self._seek(0)