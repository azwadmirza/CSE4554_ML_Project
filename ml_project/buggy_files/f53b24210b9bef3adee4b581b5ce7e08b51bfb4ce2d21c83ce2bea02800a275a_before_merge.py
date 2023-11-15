    def __init__(self, env=None, fm=None):  # pylint: disable=super-init-not-called
        self.keybuffer = KeyBuffer()
        self.keymaps = KeyMaps(self.keybuffer)
        self.redrawlock = threading.Event()
        self.redrawlock.set()

        self.titlebar = None
        self._viewmode = None
        self.taskview = None
        self.status = None
        self.console = None
        self.pager = None
        self.multiplexer = None
        self._draw_title = None
        self._tmux_automatic_rename = None
        self._tmux_title = None
        self._screen_title = None
        self.browser = None

        if fm is not None:
            self.fm = fm