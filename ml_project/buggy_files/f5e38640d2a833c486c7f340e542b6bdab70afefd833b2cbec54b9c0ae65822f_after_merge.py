    def __init__(self, frame, message="", data=None, modal=True, Search=True):

        gtk.Dialog.__init__(self)
        self.connect("destroy", self.quit)
        self.connect("delete-event", self.quit)
        self.nicotine = frame

        if modal:
            self.set_modal(True)

        self.Search = Search

        self.box = gtk.VBox(spacing=10)
        self.box.set_border_width(10)
        self.box.show()
        self.vbox.pack_start(self.box, False, False, 0)

        if message:
            label = gtk.Label()
            label.set_markup(message)
            label.set_line_wrap(False)
            self.box.pack_start(label, False, False, 0)
            label.show()
            label.set_alignment(0, 0.5)

        self.current = 0
        self.data = data

        hbox2 = gtk.HBox(spacing=5)
        hbox2.show()

        self.UF = gtk.Frame()
        self.UF.show()
        self.UF.set_shadow_type(gtk.ShadowType.ETCHED_IN)
        self.box.pack_start(self.UF, False, False, 0)

        vbox3 = gtk.VBox(spacing=5)
        vbox3.set_border_width(5)
        vbox3.show()

        self.UF.add(vbox3)

        self.UsernameLabel, self.Username = self.MakeLabelStaticEntry(
            hbox2,
            "<b>%s:</b>" % _("Username"),
            "",
            expand=False
        )

        self.BrowseUser = self.nicotine.CreateIconButton(
            gtk.STOCK_HARDDISK,
            "stock",
            self.OnBrowseUser, _("Browse")
        )

        hbox2.pack_start(self.BrowseUser, False, False, 0)

        self.PositionLabel, self.Position = self.MakeLabelStaticEntry(
            hbox2,
            _("<b>List Position:</b>"),
            "",
            expand=False,
            width=7,
            xalign=1
        )

        vbox3.pack_start(hbox2, False, False, 0)

        hbox3 = gtk.HBox(spacing=5)
        hbox3.show()
        vbox3.pack_start(hbox3, False, False, 0)

        self.FilenameLabel, self.Filename = self.MakeLabelStaticEntry(
            hbox3,
            _("<b>File Name:</b>"),
            "",
            fill=True
        )

        hbox5 = gtk.HBox(spacing=5)
        hbox5.show()
        vbox3.pack_start(hbox5, False, False, 0)

        self.DirectoryLabel, self.Directory = self.MakeLabelStaticEntry(
            hbox5,
            _("<b>Directory:</b>"),
            "",
            fill=True
        )

        self.Media = gtk.Frame()
        self.Media.show()
        self.Media.set_shadow_type(gtk.ShadowType.ETCHED_IN)
        hbox6 = gtk.HBox(spacing=5, homogeneous=False)
        hbox6.set_border_width(5)
        hbox6.show()

        self.SizeLabel, self.Size = self.MakeLabelStaticEntry(
            hbox6,
            _("<b>File Size:</b>"),
            "",
            expand=False,
            width=11,
            xalign=1
        )

        self.LengthLabel, self.Length = self.MakeLabelStaticEntry(
            hbox6,
            _("<b>Length:</b>"),
            "",
            expand=False,
            width=7,
            xalign=0.5
        )

        self.BitrateLabel, self.Bitrate = self.MakeLabelStaticEntry(
            hbox6,
            _("<b>Bitrate:</b>"),
            "",
            expand=False,
            width=12,
            xalign=0.5
        )

        self.Media.add(hbox6)
        self.box.pack_start(self.Media, False, False, 0)

        hbox7 = gtk.HBox(spacing=5, homogeneous=False)
        hbox7.show()
        self.box.pack_start(hbox7, False, False, 0)

        self.ImmediateLabel, self.Immediate = self.MakeLabelStaticEntry(
            hbox7,
            _("<b>Immediate Downloads:</b>"),
            "",
            expand=False,
            width=6,
            xalign=0.5
        )

        self.QueueLabel, self.Queue = self.MakeLabelStaticEntry(
            hbox7,
            _("<b>Queue:</b>"),
            "",
            expand=False,
            width=6,
            xalign=1
        )

        hbox4 = gtk.HBox(spacing=5, homogeneous=False)
        hbox4.show()
        self.box.pack_start(hbox4, False, False, 0)

        self.SpeedLabel, self.Speed = self.MakeLabelStaticEntry(
            hbox4,
            _("<b>Last Speed:</b>"),
            "",
            expand=False,
            width=11,
            xalign=1
        )

        self.Country = gtk.Label()
        self.Country.hide()

        hbox4.pack_start(self.Country, False, False, 0)

        self.buttonbox = gtk.HBox(False, 2)
        self.buttonbox.show()
        self.buttonbox.set_spacing(2)

        self.box.pack_start(self.buttonbox, False, False, 0)

        # Download Button
        self.DownloadItem = self.nicotine.CreateIconButton(
            gtk.STOCK_GO_DOWN,
            "stock",
            self.OnDownloadItem,
            _("Download")
        )

        self.buttonbox.pack_start(self.DownloadItem, False, False, 0)

        # Download All Button
        self.DownloadAll = self.nicotine.CreateIconButton(
            gtk.STOCK_GO_DOWN,
            "stock",
            self.OnDownloadAll,
            _("Download All")
        )

        self.buttonbox.pack_start(self.DownloadAll, False, False, 0)

        self.Selected = self.MakeLabel(
            self.buttonbox,
            _("<b>%s</b> File(s) Selected") % len(self.data),
            expand=False,
            xalign=1
        )

        self.Previous = self.nicotine.CreateIconButton(
            gtk.STOCK_GO_BACK,
            "stock",
            self.OnPrevious,
            _("Previous")
        )

        self.Next = self.nicotine.CreateIconButton(
            gtk.STOCK_GO_FORWARD,
            "stock",
            self.OnNext,
            _("Next")
        )

        self.buttonbox.pack_end(self.Next, False, False, 0)
        self.buttonbox.pack_end(self.Previous, False, False, 0)

        button = self.nicotine.CreateIconButton(
            gtk.STOCK_CLOSE,
            "stock",
            self.click,
            _("Close")
        )

        button.props.can_default = True
        self.action_area.pack_start(button, False, False, 0)

        button.grab_default()

        self.ret = None

        self.Display(self.current)