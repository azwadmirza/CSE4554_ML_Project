    def _bitmap(self, header=0, offset=0):
        """ Read relevant info about the BMP """
        read, seek = self.fp.read, self.fp.seek
        if header:
            seek(header)
        file_info = dict()
        file_info['header_size'] = i32(read(4))  # read bmp header size @offset 14 (this is part of the header size)
        file_info['direction'] = -1
        # --------------------- If requested, read header at a specific position
        header_data = ImageFile._safe_read(self.fp, file_info['header_size'] - 4)  # read the rest of the bmp header, without its size
        # --------------------------------------------------- IBM OS/2 Bitmap v1
        # ------ This format has different offsets because of width/height types
        if file_info['header_size'] == 12:
            file_info['width'] = i16(header_data[0:2])
            file_info['height'] = i16(header_data[2:4])
            file_info['planes'] = i16(header_data[4:6])
            file_info['bits'] = i16(header_data[6:8])
            file_info['compression'] = self.RAW
            file_info['palette_padding'] = 3
        # ---------------------------------------------- Windows Bitmap v2 to v5
        elif file_info['header_size'] in (40, 64, 108, 124):  # v3, OS/2 v2, v4, v5
            if file_info['header_size'] >= 40:  # v3 and OS/2
                file_info['y_flip'] = i8(header_data[7]) == 0xff
                file_info['direction'] = 1 if file_info['y_flip'] else -1
                file_info['width'] = i32(header_data[0:4])
                file_info['height'] = i32(header_data[4:8]) if not file_info['y_flip'] else 2**32 - i32(header_data[4:8])
                file_info['planes'] = i16(header_data[8:10])
                file_info['bits'] = i16(header_data[10:12])
                file_info['compression'] = i32(header_data[12:16])
                file_info['data_size'] = i32(header_data[16:20])  # byte size of pixel data
                file_info['pixels_per_meter'] = (i32(header_data[20:24]), i32(header_data[24:28]))
                file_info['colors'] = i32(header_data[28:32])
                file_info['palette_padding'] = 4
                self.info["dpi"] = tuple(
                    map(lambda x: int(math.ceil(x / 39.3701)),
                        file_info['pixels_per_meter']))
                if file_info['compression'] == self.BITFIELDS:
                    if len(header_data) >= 52:
                        for idx, mask in enumerate(['r_mask', 'g_mask', 'b_mask', 'a_mask']):
                            file_info[mask] = i32(header_data[36+idx*4:40+idx*4])
                    else:
                        for mask in ['r_mask', 'g_mask', 'b_mask', 'a_mask']:
                            file_info[mask] = i32(read(4))
                    file_info['rgb_mask'] = (file_info['r_mask'], file_info['g_mask'], file_info['b_mask'])
                    file_info['rgba_mask'] = (file_info['r_mask'], file_info['g_mask'], file_info['b_mask'], file_info['a_mask'])
        else:
            raise IOError("Unsupported BMP header type (%d)" % file_info['header_size'])
        # ------------------ Special case : header is reported 40, which
        # ---------------------- is shorter than real size for bpp >= 16
        self.size = file_info['width'], file_info['height']
        # -------- If color count was not found in the header, compute from bits
        file_info['colors'] = file_info['colors'] if file_info.get('colors', 0) else (1 << file_info['bits'])
        # -------------------------------- Check abnormal values for DOS attacks
        if file_info['width'] * file_info['height'] > 2**31:
            raise IOError("Unsupported BMP Size: (%dx%d)" % self.size)
        # ----------------------- Check bit depth for unusual unsupported values
        self.mode, raw_mode = BIT2MODE.get(file_info['bits'], (None, None))
        if self.mode is None:
            raise IOError("Unsupported BMP pixel depth (%d)" % file_info['bits'])
        # ----------------- Process BMP with Bitfields compression (not palette)
        if file_info['compression'] == self.BITFIELDS:
            SUPPORTED = {
                32: [(0xff0000, 0xff00, 0xff, 0x0), (0xff0000, 0xff00, 0xff, 0xff000000), (0x0, 0x0, 0x0, 0x0)],
                24: [(0xff0000, 0xff00, 0xff)],
                16: [(0xf800, 0x7e0, 0x1f), (0x7c00, 0x3e0, 0x1f)]
            }
            MASK_MODES = {
                (32, (0xff0000, 0xff00, 0xff, 0x0)): "BGRX",
                (32, (0xff0000, 0xff00, 0xff, 0xff000000)): "BGRA",
                (32, (0x0, 0x0, 0x0, 0x0)): "BGRA",
                (24, (0xff0000, 0xff00, 0xff)): "BGR",
                (16, (0xf800, 0x7e0, 0x1f)): "BGR;16",
                (16, (0x7c00, 0x3e0, 0x1f)): "BGR;15"
            }
            if file_info['bits'] in SUPPORTED:
                if file_info['bits'] == 32 and file_info['rgba_mask'] in SUPPORTED[file_info['bits']]:
                    raw_mode = MASK_MODES[(file_info['bits'], file_info['rgba_mask'])]
                    self.mode = "RGBA" if raw_mode in ("BGRA",) else self.mode
                elif file_info['bits'] in (24, 16) and file_info['rgb_mask'] in SUPPORTED[file_info['bits']]:
                    raw_mode = MASK_MODES[(file_info['bits'], file_info['rgb_mask'])]
                else:
                    raise IOError("Unsupported BMP bitfields layout")
            else:
                raise IOError("Unsupported BMP bitfields layout")
        elif file_info['compression'] == self.RAW:
            if file_info['bits'] == 32 and header == 22:  # 32-bit .cur offset
                raw_mode, self.mode = "BGRA", "RGBA"
        else:
            raise IOError("Unsupported BMP compression (%d)" % file_info['compression'])
        # ---------------- Once the header is processed, process the palette/LUT
        if self.mode == "P":  # Paletted for 1, 4 and 8 bit images
            # ----------------------------------------------------- 1-bit images
            if not (0 < file_info['colors'] <= 65536):
                raise IOError("Unsupported BMP Palette size (%d)" % file_info['colors'])
            else:
                padding = file_info['palette_padding']
                palette = read(padding * file_info['colors'])
                greyscale = True
                indices = (0, 255) if file_info['colors'] == 2 else list(range(file_info['colors']))
                # ------------------ Check if greyscale and ignore palette if so
                for ind, val in enumerate(indices):
                    rgb = palette[ind*padding:ind*padding + 3]
                    if rgb != o8(val) * 3:
                        greyscale = False
                # -------- If all colors are grey, white or black, ditch palette
                if greyscale:
                    self.mode = "1" if file_info['colors'] == 2 else "L"
                    raw_mode = self.mode
                else:
                    self.mode = "P"
                    self.palette = ImagePalette.raw("BGRX" if padding == 4 else "BGR", palette)

        # ----------------------------- Finally set the tile data for the plugin
        self.info['compression'] = file_info['compression']
        self.tile = [('raw', (0, 0, file_info['width'], file_info['height']), offset or self.fp.tell(),
                      (raw_mode, ((file_info['width'] * file_info['bits'] + 31) >> 3) & (~3), file_info['direction'])
                      )]