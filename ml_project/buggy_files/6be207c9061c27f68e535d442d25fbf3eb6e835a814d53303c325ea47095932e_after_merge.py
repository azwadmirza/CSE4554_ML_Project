    def __init__(self, master):
        self.master = master
        low, high = [], []
        for k, v in palettes.palettes.items():
            if v.high:
                high.append(k)
            else:
                low.append(k)
        high.sort()
        low.sort()

        options = [
            select.Heading("High Colour")
        ]

        def mkopt(name):
            return select.Option(
                i,
                None,
                lambda: self.master.options.console_palette == name,
                lambda: setattr(self.master.options, "console_palette", name)
            )

        for i in high:
            options.append(mkopt(i))
        options.append(select.Heading("Low Colour"))
        for i in low:
            options.append(mkopt(i))

        options.extend(
            [
                select.Heading("Options"),
                select.Option(
                    "Transparent",
                    "T",
                    lambda: master.options.console_palette_transparent,
                    master.options.toggler("console_palette_transparent")
                )
            ]
        )

        self.lb = select.Select(options)
        title = urwid.Text("Palettes")
        title = urwid.Padding(title, align="left", width=("relative", 100))
        title = urwid.AttrWrap(title, "heading")
        self._w = urwid.Frame(
            self.lb,
            header = title
        )
        master.options.changed.connect(self.sig_options_changed)