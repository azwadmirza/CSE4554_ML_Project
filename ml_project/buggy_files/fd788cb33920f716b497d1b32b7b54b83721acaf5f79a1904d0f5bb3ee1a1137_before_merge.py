    def __init__(self, annotation, choices=None, value='', name=''):
        wx.Panel.__init__(self, annotation, name=name)
        if choices is None:
            choices = []
        self.orig_choices = choices
        self.IDs = [wx.NewId() for c in choices]
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.combo_dlg = wx.ComboBox(
                self, choices=[choice[0] for choice in choices],
                value=value, style=wx.CB_READONLY)
        self.annotation_dlg = wx.StaticText(self, label='', style=wx.ST_NO_AUTORESIZE)
        self.annotation_dlg.MinSize = (
            max([self.annotation_dlg.GetTextExtent(choice[1] + " (from #00)")[0]
                 for choice in self.orig_choices]), -1)
        self.update_annotation()

        sizer.AddStretchSpacer()
        sizer.Add(self.combo_dlg, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, border=3)
        sizer.Add((5, 5))
        sizer.Add(self.annotation_dlg, flag=wx.ALIGN_CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)

        self.combo_dlg.Bind(wx.EVT_COMBOBOX, self.choice_made)
        self.combo_dlg.Bind(wx.EVT_RIGHT_DOWN, self.right_menu)
        for child in self.combo_dlg.Children:
            # Mac implements read_only combobox as a choice in a child
            child.Bind(wx.EVT_RIGHT_DOWN, self.right_menu)
        self.Bind(wx.EVT_MENU, self.menu_selected)
        self.callbacks = []