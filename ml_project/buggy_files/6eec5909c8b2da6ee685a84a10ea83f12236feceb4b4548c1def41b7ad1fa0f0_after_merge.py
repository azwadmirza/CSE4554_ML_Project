    def __init__(self, frame, id=-1):
        """A panel that displays available components.
        """
        self.frame = frame
        self.app = frame.app
        self.dpi = self.app.dpi
        panelWidth = 3 * 48 + 50
        scrolledpanel.ScrolledPanel.__init__(self,
                                             frame,
                                             id,
                                             size=(panelWidth, 10 * self.dpi),
                                             style=wx.BORDER_NONE)
        self._maxBtnWidth = 0  # will store width of widest button
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.componentButtons = []
        self.components = experiment.getAllComponents(
            self.app.prefs.builder['componentsFolders'])
        categories = ['Favorites']
        categories.extend(components.getAllCategories(
            self.app.prefs.builder['componentsFolders']))
        # get rid of hidden components
        for hiddenComp in self.frame.prefs['hiddenComponents']:
            if hiddenComp in self.components:
                del self.components[hiddenComp]
        # also remove settings - that's in toolbar not components panel
        del self.components['SettingsComponent']
        # get favorites
        self.favorites = FavoriteComponents(componentsPanel=self)
        # create labels and sizers for each category
        self.componentFromID = {}
        self.panels = {}
        # to keep track of the objects (sections and section labels)
        # within the main sizer
        self.sizerList = []

        for categ in categories:
            if categ in _localized:
                label = _localized[categ]
            else:
                label = categ
            _style = platebtn.PB_STYLE_DROPARROW | platebtn.PB_STYLE_SQUARE
            sectionBtn = PsychopyPlateBtn(self, -1, label, style=_style, name=categ)
            # Link to onclick functions
            sectionBtn.Bind(wx.EVT_LEFT_DOWN, self.onSectionBtn)
            sectionBtn.Bind(wx.EVT_RIGHT_DOWN, self.onSectionBtn)
            # Set button background and link to onhover functions
            #sectionBtn.Bind(wx.EVT_ENTER_WINDOW, self.onHover)
            #sectionBtn.Bind(wx.EVT_LEAVE_WINDOW, self.offHover)
            self.panels[categ] = wx.FlexGridSizer(cols=1)
            self.sizer.Add(sectionBtn, flag=wx.EXPAND)
            self.sizerList.append(sectionBtn)
            self.sizer.Add(self.panels[categ], flag=wx.ALIGN_CENTER)
            self.sizerList.append(self.panels[categ])
        maxWidth = self.makeComponentButtons()
        self._rightClicked = None
        # start all except for Favorites collapsed
        for section in categories[1:]:
            self.toggleSection(self.panels[section])

        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.SetupScrolling()
        # double buffered better rendering except if retina
        self.SetDoubleBuffered(not self.frame.isRetina)
        self._applyAppTheme()  # bitmaps only just loaded