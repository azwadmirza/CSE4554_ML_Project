    def __init__(self, frame, id=-1):
        """A panel that shows how the routines will fit together
        """
        self.frame = frame
        self.app = frame.app
        self.dpi = self.app.dpi
        wx.ScrolledWindow.__init__(self, frame, id, (0, 0),
                                   size=wx.Size(8 * self.dpi, 3 * self.dpi),
                                   style=wx.HSCROLL | wx.VSCROLL | wx.BORDER_NONE)
        self.needUpdate = True
        self.maxWidth = 50 * self.dpi
        self.maxHeight = 2 * self.dpi
        self.mousePos = None
        # if we're adding a loop or routine then add spots to timeline
        # self.drawNearestRoutinePoint = True
        # self.drawNearestLoopPoint = False
        # lists the x-vals of points to draw, eg loop locations:
        self.pointsToDraw = []
        # for flowSize, showLoopInfoInFlow:
        self.appData = self.app.prefs.appData

        # self.SetAutoLayout(True)
        self.SetScrollRate(self.dpi / 4, self.dpi / 4)

        # create a PseudoDC to record our drawing
        self.pdc = PseudoDC()
        if parse_version(wx.__version__) < parse_version('4.0.0a1'):
            self.pdc.DrawRoundedRectangle = self.pdc.DrawRoundedRectangleRect
        self.pen_cache = {}
        self.brush_cache = {}
        # vars for handling mouse clicks
        self.hitradius = 5
        self.dragid = -1
        self.entryPointPosList = []
        self.entryPointIDlist = []
        self.gapsExcluded = []
        # mode can also be 'loopPoint1','loopPoint2','routinePoint'
        self.mode = 'normal'
        self.insertingRoutine = ""

        # for the context menu use the ID of the drawn icon to retrieve
        # the component (loop or routine)
        self.componentFromID = {}
        self.contextMenuLabels = {
            'remove': _translate('remove'),
            'rename': _translate('rename')}
        self.contextMenuItems = ['remove', 'rename']
        self.contextItemFromID = {}
        self.contextIDFromItem = {}
        for item in self.contextMenuItems:
            id = wx.NewIdRef()
            self.contextItemFromID[id] = item
            self.contextIDFromItem[item] = id

        # self.btnInsertRoutine = wx.Button(self,-1,
        #                                  'Insert Routine', pos=(10,10))
        # self.btnInsertLoop = wx.Button(self,-1,'Insert Loop', pos=(10,30))
        labelRoutine = _translate('Insert Routine ')
        labelLoop = _translate('Insert Loop     ')
        btnHeight = 50
        # Create add routine button
        self.btnInsertRoutine = PsychopyPlateBtn(
            self, -1, labelRoutine, pos=(10, 10), size=(120, btnHeight),
            style=platebtn.PB_STYLE_SQUARE
        )
        # Create add loop button
        self.btnInsertLoop = PsychopyPlateBtn(
            self, -1, labelLoop, pos=(10, btnHeight+20),
            size=(120, btnHeight),
            style=platebtn.PB_STYLE_SQUARE
        )  # spaces give size for CANCEL

        # use self.appData['flowSize'] to index a tuple to get a specific
        # value, eg: (4,6,8)[self.appData['flowSize']]
        self.flowMaxSize = 2  # upper limit on increaseSize

        # bind events
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_BUTTON, self.onInsertRoutine, self.btnInsertRoutine)
        self.Bind(wx.EVT_BUTTON, self.setLoopPoint1, self.btnInsertLoop)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        idClear = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self.clearMode, id=idClear)
        aTable = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, idClear)
        ])
        self.SetAcceleratorTable(aTable)

        # double buffered better rendering except if retina
        self.SetDoubleBuffered(self.frame.IsDoubleBuffered())

        self._applyAppTheme()