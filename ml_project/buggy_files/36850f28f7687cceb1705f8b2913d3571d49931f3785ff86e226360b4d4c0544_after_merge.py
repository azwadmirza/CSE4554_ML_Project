    def __init__(self, parent):
        QTreeWidgetItem.__init__(self, parent)
        self.download_info = None
        self._logger = logging.getLogger('TriblerGUI')

        bar_container = QWidget()
        bar_container.setLayout(QVBoxLayout())
        bar_container.setStyleSheet("background-color: transparent;")

        self.progress_slider = QProgressBar()
        self.progress_slider.setStyleSheet("""
        QProgressBar {
            background-color: white;
            color: black;
            font-size: 12px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #e67300;
        }
        """)

        bar_container.layout().addWidget(self.progress_slider)
        bar_container.layout().setContentsMargins(4, 4, 8, 4)

        parent.setItemWidget(self, 2, bar_container)
        self.progress_slider.setAutoFillBackground(True)