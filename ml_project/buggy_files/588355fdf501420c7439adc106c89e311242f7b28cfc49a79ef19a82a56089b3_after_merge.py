    def __init__(self, *, win_id, mode_manager, private, parent=None):
        super().__init__(win_id=win_id, mode_manager=mode_manager,
                         private=private, parent=parent)
        widget = webview.WebEngineView(tabdata=self.data, win_id=win_id,
                                       private=private)
        self.history = WebEngineHistory(self)
        self.scroller = WebEngineScroller(self, parent=self)
        self.caret = WebEngineCaret(mode_manager=mode_manager,
                                    tab=self, parent=self)
        self.zoom = WebEngineZoom(tab=self, parent=self)
        self.search = WebEngineSearch(parent=self)
        self.printing = WebEnginePrinting()
        self.elements = WebEngineElements(tab=self)
        self.action = WebEngineAction(tab=self)
        # We're assigning settings in _set_widget
        self.settings = webenginesettings.WebEngineSettings(settings=None)
        self._set_widget(widget)
        self._connect_signals()
        self.backend = usertypes.Backend.QtWebEngine
        self._child_event_filter = None
        self._saved_zoom = None
        self._reload_url = None
        config.instance.changed.connect(self._on_config_changed)
        self._init_js()