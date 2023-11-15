    def __init__(self, settings):
        QMainWindow.__init__(self)

        self.request_mgr = None
        self.cpu_plot = None
        self.memory_plot = None
        self.initialized_cpu_plot = False
        self.initialized_memory_plot = False
        self.cpu_plot_timer = None
        self.memory_plot_timer = None

        uic.loadUi(get_ui_file_path('debugwindow.ui'), self)
        self.setWindowTitle("Tribler debug pane")

        self.window().dump_memory_core_button.clicked.connect(lambda: self.on_memory_dump_button_clicked(True))
        self.window().dump_memory_gui_button.clicked.connect(lambda: self.on_memory_dump_button_clicked(False))

        self.window().debug_tab_widget.setCurrentIndex(0)
        self.window().dispersy_tab_widget.setCurrentIndex(0)
        self.window().system_tab_widget.setCurrentIndex(0)
        self.window().debug_tab_widget.currentChanged.connect(self.tab_changed)
        self.window().dispersy_tab_widget.currentChanged.connect(self.dispersy_tab_changed)
        self.window().events_tree_widget.itemClicked.connect(self.on_event_clicked)
        self.window().system_tab_widget.currentChanged.connect(self.system_tab_changed)
        self.load_general_tab()

        self.window().open_files_tree_widget.header().setSectionResizeMode(0, QHeaderView.Stretch)

        if not settings['trustchain']['enabled']:
            self.window().debug_tab_widget.setTabEnabled(2, False)

        # Refresh logs
        self.window().log_refresh_button.clicked.connect(lambda: self.load_logs_tab())