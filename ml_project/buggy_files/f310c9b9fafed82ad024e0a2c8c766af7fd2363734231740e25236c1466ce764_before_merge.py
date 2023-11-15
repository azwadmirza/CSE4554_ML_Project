    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Color Picker", pos=wx.DefaultPosition,
                           style=wx.DEFAULT_DIALOG_STYLE)
        # Set main params
        self.color = Color((0,0,0,1), 'rgba')
        self.sizer = wx.GridBagSizer()
        # Add colourful top bar
        self.preview = ColorPreview(color=self.color, parent=self)
        self.sizer.Add(self.preview, pos=(0,0), span=wx.GBSpan(2,1), border=5, flag=wx.RIGHT | wx.EXPAND)
        # Add notebook of controls
        self.ctrls = aui.AuiNotebook(self, wx.ID_ANY, size=wx.Size(400, 400))
        self.sizer.Add(self.ctrls, pos=(0,1), border=5, flag=wx.ALL)
        self.ctrls.AddPage(ColorPage(self.ctrls, self, 'rgba'), 'RGB (-1 to 1)')
        self.ctrls.AddPage(ColorPage(self.ctrls, self, 'rgba1'), 'RGB (0 to 1)')
        self.ctrls.AddPage(ColorPage(self.ctrls, self, 'rgba255'), 'RGB (0 to 255)')
        self.ctrls.AddPage(ColorPage(self.ctrls, self, 'hsva'), 'HSV')
        self.ctrls.AddPage(ColorPage(self.ctrls, self, 'hex'), 'Hex')
        # Add array of named colours
        self.presets = ColorPresets(parent=self)
        self.sizer.Add(self.presets, pos=(0,2), border=5, flag=wx.ALL)
        # Add buttons
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.closeButton = wx.Button(self, label="Close")
        self.closeButton.Bind(wx.EVT_BUTTON, self.Close)
        self.buttons.Add(self.closeButton, border=5, flag=wx.ALL)
        # Add insert buttons
        # self.insertValueButton = wx.Button(self, label="Insert As Value")
        # self.insertValueButton.Bind(wx.EVT_BUTTON, self.insertValue)
        # self.buttons.Add(self.insertValueButton, border=5, flag=wx.ALL)
        # self.insertObjectButton = wx.Button(self, label="Insert As Object")
        # self.insertObjectButton.Bind(wx.EVT_BUTTON, self.insertObject)
        # self.buttons.Add(self.insertObjectButton, border=5, flag=wx.ALL)
        # Add copy buttons
        self.copyValueButton = wx.Button(self, label="Copy As Value")
        self.copyValueButton.Bind(wx.EVT_BUTTON, self.copyValue)
        self.buttons.Add(self.copyValueButton, border=5, flag=wx.ALL)
        self.copyObjectButton = wx.Button(self, label="Copy As Object")
        self.copyObjectButton.Bind(wx.EVT_BUTTON, self.copyObject)
        self.buttons.Add(self.copyObjectButton, border=5, flag=wx.ALL)

        self.sizer.Add(self.buttons, pos=(1,1), span=wx.GBSpan(1,2), border=5, flag=wx.ALL | wx.ALIGN_RIGHT)

        # Configure sizer
        self.sizer.AddGrowableRow(0)
        self.sizer.AddGrowableCol(1)
        self.SetSizerAndFit(self.sizer)
        self._applyAppTheme()
        self._applyAppTheme(self.ctrls)

        self.Layout()
        self.Centre(wx.BOTH)
        self.Show(True)