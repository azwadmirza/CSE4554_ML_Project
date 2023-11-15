    def __init__(self, parent, wxid=wx.ID_ANY, style=0, agwStyle=0):
        ULC.UltimateListCtrl.__init__(self, parent, wxid, wx.DefaultPosition, wx.DefaultSize, style, agwStyle)

        self.guiutility = GUIUtility.getInstance()
        self.boosting_manager = self.guiutility.utility.session.lm.boosting_manager

        self.channel_list = {}

        self._logger = logging.getLogger(self.__class__.__name__)

        self.InsertColumn(0, 'col')
        self.SetColumnWidth(0, -3)

        # index holder for labels. 0 for RSS, 1 for directory, 2 for channel
        self.labels = [0, 1, 2]

        self.InsertStringItem(self.labels[0], "RSS")
        item = self.GetItem(self.labels[0])
        item.Enable(False)
        item.SetData("RSS")
        self.SetItem(item)

        self.InsertStringItem(self.labels[1], "Directory")
        item = self.GetItem(self.labels[1])
        item.Enable(False)
        item.SetData("Directory")
        self.SetItem(item)

        self.InsertStringItem(self.labels[2], "Channel")
        item = self.GetItem(self.labels[2])
        item.Enable(False)
        item.SetData("Channel")
        self.SetItem(item)

        self.Bind(EVT_LIST_ITEM_CHECKED, self.OnGetItemCheck)

        self.getting_channels = False
        self._mainWin.Bind(wx.EVT_SCROLLWIN, self.on_scroll)