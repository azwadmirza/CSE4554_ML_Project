    def __init__(self, qt_viewer, *, show=True):

        self.qt_viewer = qt_viewer

        self._qt_window = QMainWindow()
        self._qt_window.setUnifiedTitleAndToolBarOnMac(True)
        self._qt_center = QWidget(self._qt_window)

        self._qt_window.setCentralWidget(self._qt_center)
        self._qt_window.setWindowTitle(self.qt_viewer.viewer.title)
        self._qt_center.setLayout(QHBoxLayout())
        self._status_bar = QStatusBar()
        self._qt_window.setStatusBar(self._status_bar)
        self._qt_window.closeEvent = self.closeEvent
        self.close = self._qt_window.close

        self._add_menubar()

        self._add_file_menu()
        self._add_view_menu()
        self._add_window_menu()
        self._add_help_menu()

        self._status_bar.showMessage('Ready')
        self._help = QLabel('')
        self._status_bar.addPermanentWidget(self._help)

        self._qt_center.layout().addWidget(self.qt_viewer)
        self._qt_center.layout().setContentsMargins(4, 0, 4, 0)

        self._update_palette(qt_viewer.viewer.palette)

        if self.qt_viewer.console.shell is not None:
            self._add_viewer_dock_widget(self.qt_viewer.dockConsole)

        self.qt_viewer.viewer.events.status.connect(self._status_changed)
        self.qt_viewer.viewer.events.help.connect(self._help_changed)
        self.qt_viewer.viewer.events.title.connect(self._title_changed)
        self.qt_viewer.viewer.events.palette.connect(
            lambda event: self._update_palette(event.palette)
        )

        if show:
            self.show()