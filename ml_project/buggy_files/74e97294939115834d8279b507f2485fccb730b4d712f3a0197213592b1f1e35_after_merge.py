    def _setup(self):
        """Setup this image object based on current tags"""

        if 0xBC01 in self.tag_v2:
            raise IOError("Windows Media Photo files not yet supported")

        # extract relevant tags
        self._compression = COMPRESSION_INFO[self.tag_v2.get(COMPRESSION, 1)]
        self._planar_configuration = self.tag_v2.get(PLANAR_CONFIGURATION, 1)

        # photometric is a required tag, but not everyone is reading
        # the specification
        photo = self.tag_v2.get(PHOTOMETRIC_INTERPRETATION, 0)

        # old style jpeg compression images most certainly are YCbCr
        if self._compression == "tiff_jpeg":
            photo = 6

        fillorder = self.tag_v2.get(FILLORDER, 1)

        if DEBUG:
            print("*** Summary ***")
            print("- compression:", self._compression)
            print("- photometric_interpretation:", photo)
            print("- planar_configuration:", self._planar_configuration)
            print("- fill_order:", fillorder)
            print("- YCbCr subsampling:", self.tag.get(530))

        # size
        xsize = self.tag_v2.get(IMAGEWIDTH)
        ysize = self.tag_v2.get(IMAGELENGTH)
        self._size = xsize, ysize

        if DEBUG:
            print("- size:", self.size)

        sampleFormat = self.tag_v2.get(SAMPLEFORMAT, (1,))
        if len(sampleFormat) > 1 and max(sampleFormat) == min(sampleFormat) == 1:
            # SAMPLEFORMAT is properly per band, so an RGB image will
            # be (1,1,1).  But, we don't support per band pixel types,
            # and anything more than one band is a uint8. So, just
            # take the first element. Revisit this if adding support
            # for more exotic images.
            sampleFormat = (1,)

        bps_tuple = self.tag_v2.get(BITSPERSAMPLE, (1,))
        extra_tuple = self.tag_v2.get(EXTRASAMPLES, ())
        if photo in (2, 6, 8):  # RGB, YCbCr, LAB
            bps_count = 3
        elif photo == 5:  # CMYK
            bps_count = 4
        else:
            bps_count = 1
        bps_count += len(extra_tuple)
        # Some files have only one value in bps_tuple,
        # while should have more. Fix it
        if bps_count > len(bps_tuple) and len(bps_tuple) == 1:
            bps_tuple = bps_tuple * bps_count

        # mode: check photometric interpretation and bits per pixel
        key = (
            self.tag_v2.prefix,
            photo,
            sampleFormat,
            fillorder,
            bps_tuple,
            extra_tuple,
        )
        if DEBUG:
            print("format key:", key)
        try:
            self.mode, rawmode = OPEN_INFO[key]
        except KeyError:
            if DEBUG:
                print("- unsupported format")
            raise SyntaxError("unknown pixel mode")

        if DEBUG:
            print("- raw mode:", rawmode)
            print("- pil mode:", self.mode)

        self.info["compression"] = self._compression

        xres = self.tag_v2.get(X_RESOLUTION, 1)
        yres = self.tag_v2.get(Y_RESOLUTION, 1)

        if xres and yres:
            resunit = self.tag_v2.get(RESOLUTION_UNIT)
            if resunit == 2:  # dots per inch
                self.info["dpi"] = int(xres + 0.5), int(yres + 0.5)
            elif resunit == 3:  # dots per centimeter. convert to dpi
                self.info["dpi"] = int(xres * 2.54 + 0.5), int(yres * 2.54 + 0.5)
            elif resunit is None:  # used to default to 1, but now 2)
                self.info["dpi"] = int(xres + 0.5), int(yres + 0.5)
                # For backward compatibility,
                # we also preserve the old behavior
                self.info["resolution"] = xres, yres
            else:  # No absolute unit of measurement
                self.info["resolution"] = xres, yres

        # build tile descriptors
        x = y = layer = 0
        self.tile = []
        self.use_load_libtiff = READ_LIBTIFF or self._compression != "raw"
        if self.use_load_libtiff:
            # Decoder expects entire file as one tile.
            # There's a buffer size limit in load (64k)
            # so large g4 images will fail if we use that
            # function.
            #
            # Setup the one tile for the whole image, then
            # use the _load_libtiff function.

            # libtiff handles the fillmode for us, so 1;IR should
            # actually be 1;I. Including the R double reverses the
            # bits, so stripes of the image are reversed.  See
            # https://github.com/python-pillow/Pillow/issues/279
            if fillorder == 2:
                # Replace fillorder with fillorder=1
                key = key[:3] + (1,) + key[4:]
                if DEBUG:
                    print("format key:", key)
                # this should always work, since all the
                # fillorder==2 modes have a corresponding
                # fillorder=1 mode
                self.mode, rawmode = OPEN_INFO[key]
            # libtiff always returns the bytes in native order.
            # we're expecting image byte order. So, if the rawmode
            # contains I;16, we need to convert from native to image
            # byte order.
            if rawmode == "I;16":
                rawmode = "I;16N"
            if ";16B" in rawmode:
                rawmode = rawmode.replace(";16B", ";16N")
            if ";16L" in rawmode:
                rawmode = rawmode.replace(";16L", ";16N")

            # Offset in the tile tuple is 0, we go from 0,0 to
            # w,h, and we only do this once -- eds
            a = (rawmode, self._compression, False, self.tag_v2.offset)
            self.tile.append(("libtiff", (0, 0, xsize, ysize), 0, a))

        elif STRIPOFFSETS in self.tag_v2 or TILEOFFSETS in self.tag_v2:
            # striped image
            if STRIPOFFSETS in self.tag_v2:
                offsets = self.tag_v2[STRIPOFFSETS]
                h = self.tag_v2.get(ROWSPERSTRIP, ysize)
                w = self.size[0]
            else:
                # tiled image
                offsets = self.tag_v2[TILEOFFSETS]
                w = self.tag_v2.get(322)
                h = self.tag_v2.get(323)

            for offset in offsets:
                if x + w > xsize:
                    stride = w * sum(bps_tuple) / 8  # bytes per line
                else:
                    stride = 0

                tile_rawmode = rawmode
                if self._planar_configuration == 2:
                    # each band on it's own layer
                    tile_rawmode = rawmode[layer]
                    # adjust stride width accordingly
                    stride /= bps_count

                a = (tile_rawmode, int(stride), 1)
                self.tile.append(
                    (
                        self._compression,
                        (x, y, min(x + w, xsize), min(y + h, ysize)),
                        offset,
                        a,
                    )
                )
                x = x + w
                if x >= self.size[0]:
                    x, y = 0, y + h
                    if y >= self.size[1]:
                        x = y = 0
                        layer += 1
        else:
            if DEBUG:
                print("- unsupported data organization")
            raise SyntaxError("unknown data organization")

        # Fix up info.
        if ICCPROFILE in self.tag_v2:
            self.info["icc_profile"] = self.tag_v2[ICCPROFILE]

        # fixup palette descriptor

        if self.mode in ["P", "PA"]:
            palette = [o8(b // 256) for b in self.tag_v2[COLORMAP]]
            self.palette = ImagePalette.raw("RGB;L", b"".join(palette))