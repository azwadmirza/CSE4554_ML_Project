    def _open(self):

        # HEAD
        s = self.fp.read(32)
        if i32(s) != 0x59a66a95:
            raise SyntaxError("not an SUN raster file")

        offset = 32

        self.size = i32(s[4:8]), i32(s[8:12])

        depth = i32(s[12:16])
        if depth == 1:
            self.mode, rawmode = "1", "1;I"
        elif depth == 8:
            self.mode = rawmode = "L"
        elif depth == 24:
            self.mode, rawmode = "RGB", "BGR"
        else:
            raise SyntaxError("unsupported mode")

        compression = i32(s[20:24])

        if i32(s[24:28]) != 0:
            length = i32(s[28:32])
            offset = offset + length
            self.palette = ImagePalette.raw("RGB;L", self.fp.read(length))
            if self.mode == "L":
                self.mode = rawmode = "P"

        stride = (((self.size[0] * depth + 7) // 8) + 3) & (~3)

        if compression == 1:
            self.tile = [("raw", (0, 0)+self.size, offset, (rawmode, stride))]
        elif compression == 2:
            self.tile = [("sun_rle", (0, 0)+self.size, offset, rawmode)]