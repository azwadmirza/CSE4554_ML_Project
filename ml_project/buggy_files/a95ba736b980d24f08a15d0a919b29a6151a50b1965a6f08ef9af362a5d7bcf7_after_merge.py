def APP(self, marker):
    #
    # Application marker.  Store these in the APP dictionary.
    # Also look for well-known application markers.

    n = i16(self.fp.read(2))-2
    s = ImageFile._safe_read(self.fp, n)

    app = "APP%d" % (marker & 15)

    self.app[app] = s  # compatibility
    self.applist.append((app, s))

    if marker == 0xFFE0 and s[:4] == b"JFIF":
        # extract JFIF information
        self.info["jfif"] = version = i16(s, 5)  # version
        self.info["jfif_version"] = divmod(version, 256)
        # extract JFIF properties
        try:
            jfif_unit = i8(s[7])
            jfif_density = i16(s, 8), i16(s, 10)
        except:
            pass
        else:
            if jfif_unit == 1:
                self.info["dpi"] = jfif_density
            self.info["jfif_unit"] = jfif_unit
            self.info["jfif_density"] = jfif_density
    elif marker == 0xFFE1 and s[:5] == b"Exif\0":
        # extract Exif information (incomplete)
        self.info["exif"] = s  # FIXME: value will change
    elif marker == 0xFFE2 and s[:5] == b"FPXR\0":
        # extract FlashPix information (incomplete)
        self.info["flashpix"] = s  # FIXME: value will change
    elif marker == 0xFFE2 and s[:12] == b"ICC_PROFILE\0":
        # Since an ICC profile can be larger than the maximum size of
        # a JPEG marker (64K), we need provisions to split it into
        # multiple markers. The format defined by the ICC specifies
        # one or more APP2 markers containing the following data:
        #   Identifying string      ASCII "ICC_PROFILE\0"  (12 bytes)
        #   Marker sequence number  1, 2, etc (1 byte)
        #   Number of markers       Total of APP2's used (1 byte)
        #   Profile data            (remainder of APP2 data)
        # Decoders should use the marker sequence numbers to
        # reassemble the profile, rather than assuming that the APP2
        # markers appear in the correct sequence.
        self.icclist.append(s)
    elif marker == 0xFFEE and s[:5] == b"Adobe":
        self.info["adobe"] = i16(s, 5)
        # extract Adobe custom properties
        try:
            adobe_transform = i8(s[1])
        except:
            pass
        else:
            self.info["adobe_transform"] = adobe_transform
    elif marker == 0xFFE2 and s[:4] == b"MPF\0":
        # extract MPO information
        self.info["mp"] = s[4:]
        # offset is current location minus buffer size
        # plus constant header size
        self.info["mpoffset"] = self.fp.tell() - n + 4

    # If DPI isn't in JPEG header, fetch from EXIF
    if "dpi" not in self.info and "exif" in self.info:
        exif = self._getexif()
        try:
            resolution_unit = exif[0x0128]
            x_resolution = exif[0x011A]
            try:
                dpi = x_resolution[0] / x_resolution[1]
            except TypeError:
                dpi = x_resolution
            if resolution_unit == 3: # cm
                # 1 dpcm = 2.54 dpi
                dpi *= 2.54
            self.info["dpi"] = dpi, dpi
        except KeyError:
            self.info["dpi"] = 72, 72