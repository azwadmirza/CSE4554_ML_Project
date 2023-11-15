    def __init__(self, parent=None, row=0, id=None, name="", value=0, min=-1, max=1, interval=0.01):
        rowh = 30
        wx.Panel.__init__(self, parent, id=id, style=wx.BORDER_NONE, name=name)
        # Store attributes
        self.color = parent.dlg.color
        self.parent = parent
        self.dlg = parent.dlg
        self.min = min
        self.max = max
        self.interval=interval
        # Make sizer
        self.sizer = wx.GridBagSizer()
        self.SetSizer(self.sizer)
        # Make label
        self.label = wx.StaticText(parent=self, label=name, size=(75,rowh), style=wx.ALIGN_RIGHT)
        self.sizer.Add(self.label, pos=(0, 0))
        self.sizer.AddGrowableCol(0, 0.25)
        # Make slider
        self.slider = wx.Slider(self, name=name, minValue=0, maxValue=255, size=(200, rowh))
        self.slider.Bind(wx.EVT_COMMAND_SCROLL_CHANGED, self.onChange)
        self.sizer.Add(self.slider, pos=(0, 1))
        self.sizer.AddGrowableCol(1, 0.5)
        # Make spinner (only for integer spaces)
        if self.parent.space in ['rgb255', 'rgba255', 'hex', 'hexa']:
            self.spinner = wx.SpinCtrl(self, name=name, min=min, max=max, size=(75,rowh-5))
            self.spinner.Bind(wx.EVT_SPIN_UP, self.spinUp)
            self.spinner.Bind(wx.EVT_SPIN_UP, self.spinDown)
            self.spinner.Bind(wx.EVT_SPINCTRL, self.onChange)
            self.sizer.Add(self.spinner, pos=(0, 2))
            self.sizer.AddGrowableCol(2, 0.25)
        # Set value
        self.value = value