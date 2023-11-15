    def __init__(self, parent, max_entries=100):
        QWidget.__init__(self, parent)
        
        self.setWindowTitle("Pylint")
        
        self.output = None
        self.error_output = None
        
        self.max_entries = max_entries
        self.rdata = []
        if osp.isfile(self.DATAPATH):
            try:
                data = pickle.loads(open(self.DATAPATH, 'rb').read())
                if data[0] == self.VERSION:
                    self.rdata = data[1:]
            except (EOFError, ImportError):
                pass

        self.filecombo = PythonModulesComboBox(self)
        
        self.start_button = create_toolbutton(self, icon=ima.icon('run'),
                                    text=_("Analyze"),
                                    tip=_("Run analysis"),
                                    triggered=self.start, text_beside_icon=True)
        self.stop_button = create_toolbutton(self,
                                             icon=ima.icon('stop'),
                                             text=_("Stop"),
                                             tip=_("Stop current analysis"),
                                             text_beside_icon=True)
        self.filecombo.valid.connect(self.start_button.setEnabled)
        self.filecombo.valid.connect(self.show_data)

        browse_button = create_toolbutton(self, icon=ima.icon('fileopen'),
                               tip=_('Select Python file'),
                               triggered=self.select_file)

        self.ratelabel = QLabel()
        self.datelabel = QLabel()
        self.log_button = create_toolbutton(self, icon=ima.icon('log'),
                                    text=_("Output"),
                                    text_beside_icon=True,
                                    tip=_("Complete output"),
                                    triggered=self.show_log)
        self.treewidget = ResultsTree(self)
        
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.filecombo)
        hlayout1.addWidget(browse_button)
        hlayout1.addWidget(self.start_button)
        hlayout1.addWidget(self.stop_button)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.ratelabel)
        hlayout2.addStretch()
        hlayout2.addWidget(self.datelabel)
        hlayout2.addStretch()
        hlayout2.addWidget(self.log_button)
        
        layout = QVBoxLayout()
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(self.treewidget)
        self.setLayout(layout)
        
        self.process = None
        self.set_running_state(False)
        self.show_data()

        if self.rdata:
            self.remove_obsolete_items()
            self.filecombo.addItems(self.get_filenames())
        else:
            self.start_button.setEnabled(False)