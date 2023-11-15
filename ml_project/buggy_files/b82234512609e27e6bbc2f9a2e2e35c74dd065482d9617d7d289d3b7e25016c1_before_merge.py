    def __init__(self, *, win_id, private, parent=None):
        if private:
            assert not qtutils.is_single_process()
        super().__init__(parent)
        self.widget = tabwidget.TabWidget(win_id, parent=self)
        self._win_id = win_id
        self._tab_insert_idx_left = 0
        self._tab_insert_idx_right = -1
        self.shutting_down = False
        self.widget.tabCloseRequested.connect(  # type: ignore
            self.on_tab_close_requested)
        self.widget.new_tab_requested.connect(self.tabopen)
        self.widget.currentChanged.connect(  # type: ignore
            self._on_current_changed)
        self.cur_fullscreen_requested.connect(self.widget.tabBar().maybe_hide)
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # WORKAROUND for https://bugreports.qt.io/browse/QTBUG-65223
        if qtutils.version_check('5.10', compiled=False):
            self.cur_load_finished.connect(self._leave_modes_on_load)
        else:
            self.cur_load_started.connect(self._leave_modes_on_load)

        # This init is never used, it is immediately thrown away in the next
        # line.
        self._undo_stack = (
            collections.deque()
        )  # type: typing.MutableSequence[typing.MutableSequence[UndoEntry]]
        self._update_stack_size()
        self._filter = signalfilter.SignalFilter(win_id, self)
        self._now_focused = None
        self.search_text = None
        self.search_options = {}  # type: typing.Mapping[str, typing.Any]
        self._local_marks = {
        }  # type: typing.MutableMapping[QUrl, typing.MutableMapping[str, int]]
        self._global_marks = {
        }  # type: typing.MutableMapping[str, typing.Tuple[int, QUrl]]
        self.default_window_icon = self.widget.window().windowIcon()
        self.is_private = private
        self.tab_deque = TabDeque()
        config.instance.changed.connect(self._on_config_changed)