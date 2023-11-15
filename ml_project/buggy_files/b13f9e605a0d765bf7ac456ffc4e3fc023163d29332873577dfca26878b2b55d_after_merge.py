    def _seek(self, frame):

        if frame == 0:
            # rewind
            self.__offset = 0
            self.dispose = None
            self.dispose_extent = [0, 0, 0, 0]  # x0, y0, x1, y1
            self.__frame = -1
            self.__fp.seek(self.__rewind)
            self._prev_im = None
            self.disposal_method = 0
        else:
            # ensure that the previous frame was loaded
            if not self.im:
                self.load()

        if frame != self.__frame + 1:
            raise ValueError("cannot seek to frame %d" % frame)
        self.__frame = frame

        self.tile = []

        self.fp = self.__fp
        if self.__offset:
            # backup to last frame
            self.fp.seek(self.__offset)
            while self.data():
                pass
            self.__offset = 0

        if self.dispose:
            self.im.paste(self.dispose, self.dispose_extent)

        from copy import copy
        self.palette = copy(self.global_palette)

        info = {}
        while True:

            s = self.fp.read(1)
            if not s or s == b";":
                break

            elif s == b"!":
                #
                # extensions
                #
                s = self.fp.read(1)
                block = self.data()
                if i8(s) == 249:
                    #
                    # graphic control extension
                    #
                    flags = i8(block[0])
                    if flags & 1:
                        info["transparency"] = i8(block[3])
                    info["duration"] = i16(block[1:3]) * 10

                    # disposal method - find the value of bits 4 - 6
                    dispose_bits = 0b00011100 & flags
                    dispose_bits = dispose_bits >> 2
                    if dispose_bits:
                        # only set the dispose if it is not
                        # unspecified. I'm not sure if this is
                        # correct, but it seems to prevent the last
                        # frame from looking odd for some animations
                        self.disposal_method = dispose_bits
                elif i8(s) == 254:
                    #
                    # comment extension
                    #
                    while block:
                        if "comment" in info:
                            info["comment"] += block
                        else:
                            info["comment"] = block
                        block = self.data()
                    continue
                elif i8(s) == 255:
                    #
                    # application extension
                    #
                    info["extension"] = block, self.fp.tell()
                    if block[:11] == b"NETSCAPE2.0":
                        block = self.data()
                        if len(block) >= 3 and i8(block[0]) == 1:
                            info["loop"] = i16(block[1:3])
                while self.data():
                    pass

            elif s == b",":
                #
                # local image
                #
                s = self.fp.read(9)

                # extent
                x0, y0 = i16(s[0:]), i16(s[2:])
                x1, y1 = x0 + i16(s[4:]), y0 + i16(s[6:])
                if x1 > self.size[0] or y1 > self.size[1]:
                    self._size = max(x1, self.size[0]), max(y1, self.size[1])
                self.dispose_extent = x0, y0, x1, y1
                flags = i8(s[8])

                interlace = (flags & 64) != 0

                if flags & 128:
                    bits = (flags & 7) + 1
                    self.palette =\
                        ImagePalette.raw("RGB", self.fp.read(3 << bits))

                # image data
                bits = i8(self.fp.read(1))
                self.__offset = self.fp.tell()
                self.tile = [("gif",
                             (x0, y0, x1, y1),
                             self.__offset,
                             (bits, interlace))]
                break

            else:
                pass
                # raise IOError, "illegal GIF tag `%x`" % i8(s)

        try:
            if self.disposal_method < 2:
                # do not dispose or none specified
                self.dispose = None
            elif self.disposal_method == 2:
                # replace with background colour
                self.dispose = Image.core.fill("P", self.size,
                                               self.info["background"])
            else:
                # replace with previous contents
                if self.im:
                    self.dispose = self.im.copy()

            # only dispose the extent in this frame
            if self.dispose:
                self.dispose = self._crop(self.dispose, self.dispose_extent)
        except (AttributeError, KeyError):
            pass

        if not self.tile:
            # self.__fp = None
            raise EOFError

        for k in ["transparency", "duration", "comment", "extension", "loop"]:
            if k in info:
                self.info[k] = info[k]
            elif k in self.info:
                del self.info[k]

        self.mode = "L"
        if self.palette:
            self.mode = "P"