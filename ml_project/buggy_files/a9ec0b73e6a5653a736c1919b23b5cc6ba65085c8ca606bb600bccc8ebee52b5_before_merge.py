    def __init__(self, parent):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._logger.debug("CreditMiningPanel: __init__")

        self.guiutility = GUIUtility.getInstance()
        self.utility = self.guiutility.utility
        self.installdir = self.utility.getPath()

        FancyPanel.__init__(self, parent, border=wx.BOTTOM)

        self.SetBorderColour(SEPARATOR_GREY)
        self.SetBackgroundColour(GRADIENT_LGREY, GRADIENT_DGREY)

        if not self.utility.session.get_creditmining_enable():
            wx.StaticText(self, -1, 'Credit mining inactive')
            return

        self.tdb = self.utility.session.open_dbhandler(NTFY_TORRENTS)
        self.boosting_manager = self.utility.session.lm.boosting_manager

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.header = self.create_header_info(self)
        if self.header:
            self.main_sizer.Add(self.header, 0, wx.EXPAND)

        self.main_splitter = wx.SplitterWindow(self, style=wx.SP_BORDER)
        self.main_splitter.SetMinimumPaneSize(300)

        self.sourcelist = CpanelCheckListCtrl(self.main_splitter, -1,
                                              agwStyle=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_VRULES | wx.LC_HRULES
                                              | wx.LC_SINGLE_SEL | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

        self.add_components(self.main_splitter)
        self.SetSizer(self.main_sizer)

        self.guiutility.utility.session.lm.threadpool.add_task(self._post_init, 2,
                                                               task_name=str(self) + "_post_init")