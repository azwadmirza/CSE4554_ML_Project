    def __init__(self, *, win_id, mode_manager, private, parent=None):
        self.private = private
        self.win_id = win_id
        self.tab_id = next(tab_id_gen)
        super().__init__(parent)

        self.registry = objreg.ObjectRegistry()
        tab_registry = objreg.get('tab-registry', scope='window',
                                  window=win_id)
        tab_registry[self.tab_id] = self
        objreg.register('tab', self, registry=self.registry)

        self.data = TabData()
        self._layout = miscwidgets.WrapperLayout(self)
        self._widget = None
        self._progress = 0
        self._has_ssl_errors = False
        self._mode_manager = mode_manager
        self._load_status = usertypes.LoadStatus.none
        self._mouse_event_filter = mouse.MouseEventFilter(
            self, parent=self)
        self.backend = None

        # FIXME:qtwebengine  Should this be public api via self.hints?
        #                    Also, should we get it out of objreg?
        hintmanager = hints.HintManager(win_id, self.tab_id, parent=self)
        objreg.register('hintmanager', hintmanager, scope='tab',
                        window=self.win_id, tab=self.tab_id)

        self.predicted_navigation.connect(self._on_predicted_navigation)