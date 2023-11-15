    def initialize_trust_page(self):
        vlayout = self.window().plot_widget.layout()
        self.trust_plot = TrustPlotMplCanvas(self.window().plot_widget, dpi=100)
        vlayout.addWidget(self.trust_plot)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_trust_statistics)
        self.refresh_timer.start(60000)

        self.window().trade_button.clicked.connect(self.on_trade_button_clicked)