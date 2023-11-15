    def __init__(self, *, win_id, private, parent=None):
        super().__init__(parent)
        self.widget = tabwidget.TabWidget(win_id, parent=self)
        self._win_id = win_id
        self._tab_insert_idx_left = 0
        self._tab_insert_idx_right = -1
        self.shutting_down = False
        self.widget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.widget.new_tab_requested.connect(self.tabopen)
        self.widget.currentChanged.connect(self.on_current_changed)
        self.cur_load_started.connect(self.on_cur_load_started)
        self.cur_fullscreen_requested.connect(self.widget.tabBar().maybe_hide)
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._undo_stack = []
        self._filter = signalfilter.SignalFilter(win_id, self)
        self._now_focused = None
        self.search_text = None
        self.search_options = {}
        self._local_marks = {}
        self._global_marks = {}
        self.default_window_icon = self.widget.window().windowIcon()
        self.private = private
        config.instance.changed.connect(self._on_config_changed)