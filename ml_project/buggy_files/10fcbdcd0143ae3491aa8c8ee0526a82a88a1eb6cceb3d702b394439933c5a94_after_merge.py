    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        TaskManager.__init__(self)
        self.guiutility = GUIUtility.getInstance()
        self.gui_image_manager = GuiImageManager.getInstance()
        self.session = self.guiutility.utility.session
        self.boosting_manager = self.session.lm.boosting_manager

        #dispersy_cid:Channel
        self.channels = {}

        #dispersy_cid:Popular Torrents
        self.chn_torrents = {}

        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.AddStretchSpacer()

        text = StaticText(self, -1, "Tribler")
        font = text.GetFont()
        font.SetPointSize(font.GetPointSize() * 3)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetForegroundColour((255, 51, 0))
        text.SetFont(font)

        if sys.platform == 'darwin':  # mac
            self.searchBox = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        else:
            self.searchBox = TextCtrlAutoComplete(self, entrycallback=parent.top_bg.complete)

        font = self.searchBox.GetFont()
        font.SetPointSize(font.GetPointSize() * 2)
        self.searchBox.SetFont(font)
        self.searchBox.Bind(wx.EVT_TEXT_ENTER, self.OnSearchKeyDown)

        if sys.platform == 'darwin':  # mac
            self.searchBox.SetMinSize((450, self.searchBox.GetTextExtent('T')[1] + 5))
        else:
            self.searchBox.SetMinSize((450, -1))
        self.searchBox.SetFocus()

        scalingSizer = wx.BoxSizer(wx.HORIZONTAL)

        search_img = GuiImageManager.getInstance().getImage(u"search.png")
        search_button = ActionButton(self, -1, search_img)
        search_button.Bind(wx.EVT_LEFT_UP, self.OnClick)

        scalingSizer.Add(self.searchBox, 0, wx.ALIGN_CENTER_VERTICAL)
        scalingSizer.AddSpacer(3, -1)
        scalingSizer.Add(search_button, 0, wx.ALIGN_CENTER_VERTICAL, 3)

        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.Add(StaticText(self, -1, "Take me to "))
        channelLink = LinkStaticText(self, "channels", icon=None)

        channelLink.Bind(wx.EVT_LEFT_UP, self.OnChannels)
        hSizer.Add(channelLink)
        hSizer.Add(StaticText(self, -1, " to see what others are sharing."))

        vSizer.Add(text, 0, wx.ALIGN_CENTER)
        vSizer.Add(scalingSizer, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP)
        vSizer.Add(hSizer, 0, wx.ALIGN_CENTER)
        vSizer.AddStretchSpacer()

        # channel panel is for popular channel
        self.channel_panel = wx.lib.scrolledpanel.ScrolledPanel(self, 1)
        self.channel_panel.SetBackgroundColour(wx.WHITE)
        self.channel_panel.SetForegroundColour(parent.GetForegroundColour())

        v_chn_sizer = wx.BoxSizer(wx.VERTICAL)
        v_chn_sizer.Add(
            DetailHeader(self.channel_panel, "Select popular channels to mine"),
            0, wx.EXPAND, 5)

        self.loading_channel_txt = wx.StaticText(self.channel_panel, 1,
                                                 'Loading, please wait.'
                                                 if self.boosting_manager else "Credit Mining inactive")

        v_chn_sizer.Add(self.loading_channel_txt, 1, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.chn_sizer = wx.FlexGridSizer(0, COLUMN_SIZE, 5, 5)

        for i in xrange(0, COLUMN_SIZE):
            if wx.MAJOR_VERSION > 2:
                if self.chn_sizer.IsColGrowable(i):
                    self.chn_sizer.AddGrowableCol(i, 1)
            else:
                self.chn_sizer.AddGrowableCol(i, 1)

        v_chn_sizer.Add(self.chn_sizer, 0, wx.EXPAND, 5)

        self.channel_panel.SetSizer(v_chn_sizer)
        self.channel_panel.SetupScrolling()

        vSizer.Add(self.channel_panel, 5, wx.EXPAND)

        # video thumbnail panel
        self.aw_panel = ArtworkPanel(self)
        self.aw_panel.SetMinSize((-1, 275))
        self.aw_panel.Show(self.guiutility.ReadGuiSetting('show_artwork', False))
        vSizer.Add(self.aw_panel, 0, wx.EXPAND)

        self.SetSizer(vSizer)
        self.Layout()
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        self.SearchFocus()

        self.channel_list_ready = False

        if self.boosting_manager:
            self.schedule_refresh_channels_home()