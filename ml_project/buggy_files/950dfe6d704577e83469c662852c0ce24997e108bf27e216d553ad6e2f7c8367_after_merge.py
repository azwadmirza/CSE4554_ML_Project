    def __init__(self, *, private, geometry=None, parent=None):
        """Create a new main window.

        Args:
            geometry: The geometry to load, as a bytes-object (or None).
            private: Whether the window is in private browsing mode.
            parent: The parent the window should get.
        """
        super().__init__(parent)
        # Late import to avoid a circular dependency
        # - browsertab -> hints -> webelem -> mainwindow -> bar -> browsertab
        from qutebrowser.mainwindow import tabbedbrowser
        from qutebrowser.mainwindow.statusbar import bar

        self.setAttribute(Qt.WA_DeleteOnClose)
        self._commandrunner = None
        self._overlays = []
        self.win_id = next(win_id_gen)
        self.registry = objreg.ObjectRegistry()
        objreg.window_registry[self.win_id] = self
        objreg.register('main-window', self, scope='window',
                        window=self.win_id)
        tab_registry = objreg.ObjectRegistry()
        objreg.register('tab-registry', tab_registry, scope='window',
                        window=self.win_id)

        message_bridge = message.MessageBridge(self)
        objreg.register('message-bridge', message_bridge, scope='window',
                        window=self.win_id)

        self.setWindowTitle('qutebrowser')
        self._vbox = QVBoxLayout(self)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)

        self._init_downloadmanager()
        self._downloadview = downloadview.DownloadView(self.win_id)

        if config.val.content.private_browsing:
            # This setting always trumps what's passed in.
            private = True
        else:
            private = bool(private)
        self._private = private
        self.tabbed_browser = tabbedbrowser.TabbedBrowser(win_id=self.win_id,
                                                          private=private,
                                                          parent=self)
        objreg.register('tabbed-browser', self.tabbed_browser, scope='window',
                        window=self.win_id)
        self._init_command_dispatcher()

        # We need to set an explicit parent for StatusBar because it does some
        # show/hide magic immediately which would mean it'd show up as a
        # window.
        self.status = bar.StatusBar(win_id=self.win_id, private=private,
                                    parent=self)

        self._add_widgets()
        self._downloadview.show()

        self._init_completion()

        log.init.debug("Initializing modes...")
        modeman.init(self.win_id, self)

        self._commandrunner = runners.CommandRunner(self.win_id,
                                                    partial_match=True)

        self._keyhint = keyhintwidget.KeyHintView(self.win_id, self)
        self._add_overlay(self._keyhint, self._keyhint.update_geometry)

        self._prompt_container = prompt.PromptContainer(self.win_id, self)
        self._add_overlay(self._prompt_container,
                          self._prompt_container.update_geometry,
                          centered=True, padding=10)
        objreg.register('prompt-container', self._prompt_container,
                        scope='window', window=self.win_id)
        self._prompt_container.hide()

        self._messageview = messageview.MessageView(parent=self)
        self._add_overlay(self._messageview, self._messageview.update_geometry)

        self._init_geometry(geometry)
        self._connect_signals()

        # When we're here the statusbar might not even really exist yet, so
        # resizing will fail. Therefore, we use singleShot QTimers to make sure
        # we defer this until everything else is initialized.
        QTimer.singleShot(0, self._connect_overlay_signals)
        config.instance.changed.connect(self._on_config_changed)

        objreg.get("app").new_window.emit(self)
        self._set_decoration(config.val.window.hide_decoration)