    def __init__(self, parent, id=-1, title='PsychoPy (Experiment Builder)',
                 pos=wx.DefaultPosition, fileName=None, frameData=None,
                 style=wx.DEFAULT_FRAME_STYLE, app=None):

        if (fileName is not None) and (type(fileName) == bytes):
            fileName = fileName.decode(sys.getfilesystemencoding())

        self.app = app
        self.dpi = self.app.dpi
        # things the user doesn't set like winsize etc:
        self.appData = self.app.prefs.appData['builder']
        # things about the builder that the user can set:
        self.prefs = self.app.prefs.builder
        self.appPrefs = self.app.prefs.app
        self.paths = self.app.prefs.paths
        self.frameType = 'builder'
        self.filename = fileName
        self.htmlPath = None
        self.project = None  # type: pavlovia.PavloviaProject
        self.btnHandles = {}  # stores toolbar buttons so they can be altered
        self.scriptProcess = None
        self.stdoutBuffer = None
        self.generateScript = generateScript

        if fileName in self.appData['frames']:
            self.frameData = self.appData['frames'][fileName]
        else:  # work out a new frame size/location
            dispW, dispH = self.app.getPrimaryDisplaySize()
            default = self.appData['defaultFrame']
            default['winW'] = int(dispW * 0.75)
            default['winH'] = int(dispH * 0.75)
            if default['winX'] + default['winW'] > dispW:
                default['winX'] = 5
            if default['winY'] + default['winH'] > dispH:
                default['winY'] = 5
            self.frameData = dict(self.appData['defaultFrame'])  # copy
            # increment default for next frame
            default['winX'] += 10
            default['winY'] += 10

        # we didn't have the key or the win was minimized / invalid
        if self.frameData['winH'] == 0 or self.frameData['winW'] == 0:
            self.frameData['winX'], self.frameData['winY'] = (0, 0)
        if self.frameData['winY'] < 20:
            self.frameData['winY'] = 20
        wx.Frame.__init__(self, parent=parent, id=id, title=title,
                          pos=(int(self.frameData['winX']), int(
                              self.frameData['winY'])),
                          size=(int(self.frameData['winW']), int(
                              self.frameData['winH'])),
                          style=style)
        self.Bind(wx.EVT_CLOSE, self.closeFrame)
        #self.panel = wx.Panel(self)

        # detect retina displays (then don't use double-buffering)
        self.isRetina = \
            self.GetContentScaleFactor() != 1 and wx.Platform == '__WXMAC__'

        # create icon
        if sys.platform != 'darwin':
            # doesn't work on darwin and not necessary: handled by app bundle
            iconFile = os.path.join(self.paths['resources'], 'builder.ico')
            if os.path.isfile(iconFile):
                self.SetIcon(wx.Icon(iconFile, wx.BITMAP_TYPE_ICO))

        # create our panels
        self.flowPanel = FlowPanel(frame=self)
        self.routinePanel = RoutinesNotebook(self)
        self.componentButtons = ComponentsPanel(self)
        # menus and toolbars
        self.toolbar = PsychopyToolbar(frame=self)
        self.SetToolBar(self.toolbar)
        self.makeMenus()
        self.CreateStatusBar()
        self.SetStatusText("")

        # setup universal shortcuts
        accelTable = self.app.makeAccelTable()
        self.SetAcceleratorTable(accelTable)

        # setup a default exp
        if fileName is not None and os.path.isfile(fileName):
            self.fileOpen(filename=fileName, closeCurrent=False)
        else:
            self.lastSavedCopy = None
            # don't try to close before opening
            self.fileNew(closeCurrent=False)
        self.updateReadme()

        # control the panes using aui manager
        self._mgr = aui.AuiManager(
            self,
            aui.AUI_MGR_DEFAULT | aui.AUI_MGR_RECTANGLE_HINT)

        #self._mgr.SetArtProvider(PsychopyDockArt())
        #self._art = self._mgr.GetArtProvider()
        # Create panels
        self._mgr.AddPane(self.routinePanel,
                          aui.AuiPaneInfo().
                          Name("Routines").Caption("Routines").CaptionVisible(True).
                          Floatable(False).
                          CloseButton(False).MaximizeButton(True).PaneBorder(False).
                          Center())  # 'center panes' expand
        rtPane = self._mgr.GetPane('Routines')
        self._mgr.AddPane(self.componentButtons,
                          aui.AuiPaneInfo().
                          Name("Components").Caption("Components").CaptionVisible(True).
                          Floatable(False).
                          RightDockable(True).LeftDockable(True).
                          CloseButton(False).PaneBorder(False))
        compPane = self._mgr.GetPane('Components')
        self._mgr.AddPane(self.flowPanel,
                          aui.AuiPaneInfo().
                          Name("Flow").Caption("Flow").CaptionVisible(True).
                          BestSize((8 * self.dpi, 2 * self.dpi)).
                          Floatable(False).
                          RightDockable(True).LeftDockable(True).
                          CloseButton(False).PaneBorder(False))
        flowPane = self._mgr.GetPane('Flow')
        self.layoutPanes()
        rtPane.CaptionVisible(True)
        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()
        # self.SetSizer(self.mainSizer)  # not necessary for aui type controls
        if self.frameData['auiPerspective']:
            self._mgr.LoadPerspective(self.frameData['auiPerspective'])
        self.SetMinSize(wx.Size(600, 400))  # min size for the whole window
        self.SetSize(
            (int(self.frameData['winW']), int(self.frameData['winH'])))
        self.SendSizeEvent()
        self._mgr.Update()

        # self.SetAutoLayout(True)
        self.Bind(wx.EVT_CLOSE, self.closeFrame)

        self.app.trackFrame(self)
        self.SetDropTarget(FileDropTarget(targetFrame=self))
        self._applyAppTheme()