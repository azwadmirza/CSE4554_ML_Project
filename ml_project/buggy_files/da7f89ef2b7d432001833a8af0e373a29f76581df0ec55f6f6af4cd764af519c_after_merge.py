    def __getattr__(self, desc):
        try:
            ds = desc.replace('gray', 'bright_black').split('_')
            init = ''
            while ds:
                d = ds[0]
                try:
                    init += self._attributes[d]
                    ds.pop(0)
                except KeyError:
                    break
            def c():
                bright = 0
                c = ds.pop(0)
                if c == 'bright':
                    c = ds.pop(0)
                    if self.has_bright:
                        bright = 8
                return self._colors[c] + bright
            if ds:
                if ds[0] == 'on':
                    ds.pop(0)
                    init += self._bg_color(c())
                else:
                    init += self._fg_color(c())
                    if len(ds):
                        assert ds.pop(0) == 'on'
                        init += self._bg_color(c())
            return self._decorator(desc, init)
        except (IndexError, KeyError):
            raise AttributeError("'module' object has no attribute %r" % desc)