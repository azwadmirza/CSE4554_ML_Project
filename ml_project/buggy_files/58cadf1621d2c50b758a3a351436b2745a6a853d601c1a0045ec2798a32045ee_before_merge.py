    def __init__(self, frame, id=-1):
        self.frame = frame
        self.app = frame.app
        self.routineMaxSize = 2
        self.appData = self.app.prefs.appData
        aui.AuiNotebook.__init__(self, frame, id)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.onClosePane)

        # double buffered better rendering except if retina
        self.SetDoubleBuffered(self.frame.IsDoubleBuffered())

        self._applyAppTheme()
        if not hasattr(self.frame, 'exp'):
            return  # we haven't yet added an exp