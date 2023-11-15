    def __init__(self, parent, ID, title, files=(), app=None):
        self.app = app  # type: PsychoPyApp
        self.frameType = 'coder'
        # things the user doesn't set like winsize etc
        self.appData = self.app.prefs.appData['coder']
        self.prefs = self.app.prefs.coder  # things about coder that get set
        self.appPrefs = self.app.prefs.app
        self.paths = self.app.prefs.paths
        self.IDs = self.app.IDs
        self.currentDoc = None
        self.project = None
        self.ignoreErrors = False
        self.fileStatusLastChecked = time.time()
        self.fileStatusCheckInterval = 5 * 60  # sec
        self.showingReloadDialog = False
        self.btnHandles = {}  # stores toolbar buttons so they can be altered

        # we didn't have the key or the win was minimized/invalid
        if self.appData['winH'] == 0 or self.appData['winW'] == 0:
            self.appData['winH'], self.appData['winW'] = wx.DefaultSize
            self.appData['winX'], self.appData['winY'] = wx.DefaultPosition
        if self.appData['winY'] < 20:
            self.appData['winY'] = 20
        # fix issue in Windows when frame was closed while iconized
        if self.appData['winX'] == -32000:
            self.appData['winX'], self.appData['winY'] = wx.DefaultPosition
            self.appData['winH'], self.appData['winW'] = wx.DefaultSize
        wx.Frame.__init__(self, parent, ID, title,
                          (self.appData['winX'], self.appData['winY']),
                          size=(self.appData['winW'], self.appData['winH']))

        # detect retina displays (then don't use double-buffering)
        self.isRetina = \
            self.GetContentScaleFactor() != 1 and wx.Platform == '__WXMAC__'

        # create a panel which the aui manager can hook onto
        szr = wx.BoxSizer(wx.VERTICAL)
        self.pnlMain = wx.Panel(self)
        szr.Add(self.pnlMain, flag=wx.EXPAND | wx.ALL, proportion=1)
        self.SetSizer(szr)

        # self.panel = wx.Panel(self)
        self.Hide()  # ugly to see it all initialise
        # create icon
        if sys.platform == 'darwin':
            pass  # doesn't work and not necessary - handled by app bundle
        else:
            iconFile = os.path.join(self.paths['resources'], 'coder.ico')
            if os.path.isfile(iconFile):
                self.SetIcon(wx.Icon(iconFile, wx.BITMAP_TYPE_ICO))
        # NB not the same as quit - just close the window
        self.Bind(wx.EVT_CLOSE, self.closeFrame)
        self.Bind(wx.EVT_IDLE, self.onIdle)

        if 'state' in self.appData and self.appData['state'] == 'maxim':
            self.Maximize()
        # initialise some attributes
        self.modulesLoaded = False  # goes true when loading thread completes
        self.findDlg = None
        self.findData = wx.FindReplaceData()
        self.findData.SetFlags(wx.FR_DOWN)
        self.importedScripts = {}
        self.scriptProcess = None
        self.scriptProcessID = None
        self.db = None  # debugger
        self._lastCaretPos = None

        # setup universal shortcuts
        accelTable = self.app.makeAccelTable()
        self.SetAcceleratorTable(accelTable)

        # Setup pane and art managers
        self.paneManager = aui.AuiManager(self.pnlMain, aui.AUI_MGR_DEFAULT | aui.AUI_MGR_RECTANGLE_HINT)
        # Create toolbar
        self.toolbar = PsychopyToolbar(self)
        self.SetToolBar(self.toolbar)
        # Create menus and status bar
        self.makeMenus()
        self.makeStatusBar()
        self.fileMenu = self.editMenu = self.viewMenu = None
        self.helpMenu = self.toolsMenu = None
        self.pavloviaMenu.syncBtn.Enable(bool(self.filename))
        self.pavloviaMenu.newBtn.Enable(bool(self.filename))
        # Link to file drop function
        self.SetDropTarget(FileDropTarget(targetFrame=self))

        # Create source assistant notebook
        self.sourceAsst = aui.AuiNotebook(
            self.pnlMain,
            wx.ID_ANY,
            size = wx.Size(350, 600),
            agwStyle=aui.AUI_NB_CLOSE_ON_ALL_TABS |
                     aui.AUI_NB_TAB_SPLIT |
                     aui.AUI_NB_TAB_MOVE)

        self.structureWindow = SourceTreePanel(self.sourceAsst, self)
        self.fileBrowserWindow = FileBrowserPanel(self.sourceAsst, self)
        # Add source assistant panel
        self.paneManager.AddPane(self.sourceAsst,
                                 aui.AuiPaneInfo().
                                 BestSize((350, 600)).
                                 FloatingSize((350, 600)).
                                 Floatable(False).
                                 BottomDockable(False).TopDockable(False).
                                 CloseButton(False).PaneBorder(False).
                                 Name("SourceAsst").
                                 Caption(_translate("Source Assistant")).
                                 Left())
        # Add structure page to source assistant
        self.structureWindow.SetName("Structure")
        self.sourceAsst.AddPage(self.structureWindow, "Structure")
        # Add file browser page to source assistant
        self.fileBrowserWindow.SetName("FileBrowser")
        self.sourceAsst.AddPage(self.fileBrowserWindow, "File Browser")

        # remove close buttons
        self.sourceAsst.SetCloseButton(0, False)
        self.sourceAsst.SetCloseButton(1, False)

        # Create editor notebook
        #todo: Why is editor default background not same as usual frame backgrounds?
        self.notebook = aui.AuiNotebook(
            self.pnlMain, -1, size=wx.Size(480, 600),
            agwStyle=aui.AUI_NB_TAB_MOVE | aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)

        #self.notebook.SetArtProvider(PsychopyTabArt())
        # Add editor panel
        self.paneManager.AddPane(self.notebook, aui.AuiPaneInfo().
                                 Name("Editor").
                                 Caption(_translate("Editor")).
                                 BestSize((480, 600)).
                                 Floatable(False).
                                 Movable(False).
                                 Center().PaneBorder(False).  # 'center panes' expand
                                 CloseButton(False).
                                 MaximizeButton(True))
        self.notebook.SetFocus()
        # Link functions
        self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.fileClose)
        self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.pageChanged)
        self.Bind(wx.EVT_FIND, self.OnFindNext)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFindNext)
        #self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        self.Bind(wx.EVT_END_PROCESS, self.onProcessEnded)

        # take files from arguments and append the previously opened files
        filename = ""
        if files not in [None, [], ()]:
            for filename in files:
                if not os.path.isfile(filename):
                    continue
                self.setCurrentDoc(filename, keepHidden=True)

        # Create shelf notebook
        self.shelf = aui.AuiNotebook(self.pnlMain, wx.ID_ANY, size=wx.Size(600, 600), agwStyle=aui.AUI_NB_CLOSE_ON_ALL_TABS)
        #self.shelf.SetArtProvider(PsychopyTabArt())
        # Create shell
        self._useShell = None
        if haveCode:
            useDefaultShell = True
            if self.prefs['preferredShell'].lower() == 'ipython':
                try:
                    # Try to use iPython
                    from IPython.gui.wx.ipython_view import IPShellWidget
                    self.shell = IPShellWidget(self)
                    useDefaultShell = False
                    self._useShell = 'ipython'
                except Exception:
                    msg = _translate('IPython failed as shell, using pyshell'
                                     ' (IPython v0.12 can fail on wx)')
                    logging.warn(msg)
            if useDefaultShell:
                # Default to Pyshell if iPython fails
                self.shell = PsychopyPyShell(self)
                self._useShell = 'pyshell'
            # Add shell to output pane
            self.shell.SetName("PythonShell")
            self.shelf.AddPage(self.shell, _translate('Shell'))
            # Hide close button
            for i in range(self.shelf.GetPageCount()):
                self.shelf.SetCloseButton(i, False)
        # Add shelf panel
        self.paneManager.AddPane(self.shelf,
                                 aui.AuiPaneInfo().
                                 Name("Shelf").
                                 Caption(_translate("Shelf")).
                                 BestSize((600, 250)).PaneBorder(False).
                                 Floatable(False).
                                 Movable(True).
                                 BottomDockable(True).TopDockable(True).
                                 CloseButton(False).
                                 Bottom())
        self._applyAppTheme()
        if 'pavloviaSync' in self.btnHandles:
            self.toolbar.EnableTool(self.btnHandles['pavloviaSync'].Id, bool(self.filename))
        self.unitTestFrame = None

        # Link to Runner output
        if self.app.runner is None:
            self.app.showRunner()
        self.outputWindow = self.app.runner.stdOut
        self.outputWindow.write(_translate('Welcome to PsychoPy3!') + '\n')
        self.outputWindow.write("v%s\n" % self.app.version)

        # Manage perspective
        if (self.appData['auiPerspective'] and
                'Shelf' in self.appData['auiPerspective']):
            self.paneManager.LoadPerspective(self.appData['auiPerspective'])
            self.paneManager.GetPane('SourceAsst').Caption(_translate("Source Assistant"))
            self.paneManager.GetPane('Editor').Caption(_translate("Editor"))
        else:
            self.SetMinSize(wx.Size(400, 600))  # min size for whole window
            self.Fit()
        # Update panes PsychopyToolbar
        isExp = filename.endswith(".py") or filename.endswith(".psyexp")

        # if the toolbar is done then adjust buttons
        if hasattr(self, 'cdrBtnRunner'):
            self.toolbar.EnableTool(self.cdrBtnRunner.Id, isExp)
            self.toolbar.EnableTool(self.cdrBtnRun.Id, isExp)
        # Hide panels as specified
        self.paneManager.GetPane("SourceAsst").Show(self.prefs['showSourceAsst'])
        self.paneManager.GetPane("Shelf").Show(self.prefs['showOutput'])
        self.paneManager.Update()
        #self.chkShowAutoComp.Check(self.prefs['autocomplete'])
        self.SendSizeEvent()
        self.app.trackFrame(self)