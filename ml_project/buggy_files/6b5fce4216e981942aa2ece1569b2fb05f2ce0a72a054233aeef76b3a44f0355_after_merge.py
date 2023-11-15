    def __init__(self, rsrcmgr, spec, strict=settings.STRICT):
        try:
            self.basefont = literal_name(spec['BaseFont'])
        except KeyError:
            if strict:
                raise PDFFontError('BaseFont is missing')
            self.basefont = 'unknown'
        self.cidsysteminfo = dict_value(spec.get('CIDSystemInfo', {}))
        self.cidcoding = '%s-%s' % (resolve1(self.cidsysteminfo.get('Registry', b'unknown')).decode("latin1"),
                                    resolve1(self.cidsysteminfo.get('Ordering', b'unknown')).decode("latin1"))
        self.cmap = self.get_cmap_from_spec(spec, strict)

        try:
            descriptor = dict_value(spec['FontDescriptor'])
        except KeyError:
            if strict:
                raise PDFFontError('FontDescriptor is missing')
            descriptor = {}
        ttf = None
        if 'FontFile2' in descriptor:
            self.fontfile = stream_value(descriptor.get('FontFile2'))
            ttf = TrueTypeFont(self.basefont,
                               BytesIO(self.fontfile.get_data()))
        self.unicode_map = None
        if 'ToUnicode' in spec:
            strm = stream_value(spec['ToUnicode'])
            self.unicode_map = FileUnicodeMap()
            CMapParser(self.unicode_map, BytesIO(strm.get_data())).run()
        elif self.cidcoding in ('Adobe-Identity', 'Adobe-UCS'):
            if ttf:
                try:
                    self.unicode_map = ttf.create_unicode_map()
                except TrueTypeFont.CMapNotFound:
                    pass
        else:
            try:
                self.unicode_map = CMapDB.get_unicode_map(self.cidcoding, self.cmap.is_vertical())
            except CMapDB.CMapNotFound as e:
                pass

        self.vertical = self.cmap.is_vertical()
        if self.vertical:
            # writing mode: vertical
            widths = get_widths2(list_value(spec.get('W2', [])))
            self.disps = dict((cid, (vx, vy)) for (cid, (_, (vx, vy))) in six.iteritems(widths))
            (vy, w) = spec.get('DW2', [880, -1000])
            self.default_disp = (None, vy)
            widths = dict((cid, w) for (cid, (w, _)) in six.iteritems(widths))
            default_width = w
        else:
            # writing mode: horizontal
            self.disps = {}
            self.default_disp = 0
            widths = get_widths(list_value(spec.get('W', [])))
            default_width = spec.get('DW', 1000)
        PDFFont.__init__(self, descriptor, widths, default_width=default_width)
        return