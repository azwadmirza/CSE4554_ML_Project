    def __init__(self, c, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setObjectName('viewrendered_pane')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.active = False
        self.c = c
        self.badColors = []
        self.delete_callback = None
        self.gnx = None
        self.inited = False
        self.gs = None # For @graphics-script: a QGraphicsScene
        self.gv = None # For @graphics-script: a QGraphicsView
        #self.kind = 'rst' # in self.dispatch_dict.keys()
        self.length = 0 # The length of previous p.b.
        self.locked = False
        self.scrollbar_pos_dict = {} # Keys are vnodes, values are positions.
        self.sizes = [] # Saved splitter sizes.
        self.splitter_index = None # The index of the rendering pane in the splitter.
        self.svg_class = QtSvg.QSvgWidget
        self.text_class = QtWidgets.QTextBrowser # QtWidgets.QTextEdit
        self.html_class = WebViewPlus #QtWebKitWidgets.QWebView
        self.graphics_class = QtWidgets.QGraphicsWidget
        self.vp = None # The present video player.
        self.w = None # The present widget in the rendering pane.
        self.title = None
        # User-options
        self.reloadSettings()
        self.node_changed = True
        # Init.
        self.create_dispatch_dict()
        self.activate()
        #---------------PMM additional elements for WebView additions for reST
        self.reflevel = 0
        # Special-mode rendering settings
        self.verbose = False
        self.output = 'html'
        self.tree = True
        self.showcode = True
        self.code_only = False
        self.execcode = False
        self.restoutput = False