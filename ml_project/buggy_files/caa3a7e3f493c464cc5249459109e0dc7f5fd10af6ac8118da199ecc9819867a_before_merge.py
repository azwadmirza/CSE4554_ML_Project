    def redraw(self):
        fc = len(self.master.view)
        if self.master.view.focus.flow is None:
            offset = 0
        else:
            offset = self.master.view.focus.index + 1

        if self.master.options.order_reversed:
            arrow = common.SYMBOL_UP
        else:
            arrow = common.SYMBOL_DOWN

        t = [
            ('heading', ("%s [%s/%s]" % (arrow, offset, fc)).ljust(11)),
        ]

        if self.master.server.bound:
            host = self.master.server.address.host
            if host == "0.0.0.0":
                host = "*"
            boundaddr = "[%s:%s]" % (host, self.master.server.address.port)
        else:
            boundaddr = ""
        t.extend(self.get_status())
        status = urwid.AttrWrap(urwid.Columns([
            urwid.Text(t),
            urwid.Text(
                [
                    self.helptext,
                    boundaddr
                ],
                align="right"
            ),
        ]), "heading")
        self.ib._w = status