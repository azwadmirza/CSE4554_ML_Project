    def __init__(self, parent, ID, frame,
                 # set the viewer to be small, then it will increase with aui
                 # control
                 pos=wx.DefaultPosition, size=wx.Size(100, 100),
                 style=wx.BORDER_NONE, readonly=False):
        BaseCodeEditor.__init__(self, parent, ID, pos, size, style)

        self.coder = frame
        self.prefs = self.coder.prefs
        self.paths = self.coder.paths
        self.app = self.coder.app
        self.SetViewWhiteSpace(self.coder.appData['showWhitespace'])
        self.SetViewEOL(self.coder.appData['showEOLs'])
        self.Bind(wx.stc.EVT_STC_MODIFIED, self.onModified)
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyReleased)

        if hasattr(self, 'OnMarginClick'):
            self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick)

        # black-and-white text signals read-only file open in Coder window
        # if not readonly:
        #     self.setFonts()
        self.SetDropTarget(FileDropTarget(targetFrame=self.coder))

        # set to python syntax code coloring
        self.setLexerFromFileName()

        # Keep track of visual aspects of the source tree viewer when working
        # with this document. This makes sure the tree maintains it's state when
        # moving between documents.
        self.expandedItems = {}

        # show the long line edge guide, enabled if >0
        self.edgeGuideColumn = self.coder.prefs['edgeGuideColumn']
        self.edgeGuideVisible = self.edgeGuideColumn > 0

        # give a little space between the margin and text
        self.SetMarginLeft(4)

        # whitespace information
        self.indentSize = self.GetIndent()
        self.newlines = '/n'

        # caret info, these are updated by calling updateCaretInfo()
        self.caretCurrentPos = self.GetCurrentPos()
        self.caretVisible, caretColumn, caretLine = self.PositionToXY(
            self.caretCurrentPos)

        if self.caretVisible:
            self.caretColumn = caretColumn
            self.caretLine = caretLine
        else:
            self.caretLine = self.GetCurrentLine()
            self.caretColumn = self.GetLineLength(self.caretLine)

        # where does the line text start?
        self.caretLineIndentCol = \
            self.GetColumn(self.GetLineIndentPosition(self.caretLine))

        # what is the indent level of the line the caret is located
        self.caretLineIndentLevel = self.caretLineIndentCol / self.indentSize

        # is the caret at an indentation level?
        self.caretAtIndentLevel = \
            (self.caretLineIndentCol % self.indentSize) == 0

        # # should hitting backspace result in an untab?
        # self.shouldBackspaceUntab = \
        #     self.caretAtIndentLevel and \
        #     0 < self.caretColumn <= self.caretLineIndentCol
        self.SetBackSpaceUnIndents(True)

        # set the current line and column in the status bar
        self.coder.SetStatusText(
            'Line: {} Col: {}'.format(
                self.caretLine + 1, self.caretColumn + 1), 1)

        # calltips
        self.CallTipSetBackground(ThemeMixin.codeColors['base']['bg'])
        self.CallTipSetForeground(ThemeMixin.codeColors['base']['fg'])
        self.CallTipSetForegroundHighlight(ThemeMixin.codeColors['select']['fg'])
        self.AutoCompSetIgnoreCase(True)
        self.AutoCompSetAutoHide(True)
        self.AutoCompStops('. ')
        self.openBrackets = 0

        # better font rendering and less flicker on Windows by using Direct2D
        # for rendering instead of GDI
        if wx.Platform == '__WXMSW__':
            self.SetTechnology(3)

        # double buffered better rendering except if retina
        self.SetDoubleBuffered(not self.coder.isRetina)

        self.theme = self.app.prefs.app['theme']