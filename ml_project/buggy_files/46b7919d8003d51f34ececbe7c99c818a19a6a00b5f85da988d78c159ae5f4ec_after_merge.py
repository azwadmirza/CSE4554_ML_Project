    def __init__(self, parent):
        QTabWidget.__init__(self, parent)
        self.current_download = None
        self.request_mgr = None
        self.files_widgets = {}    # dict of file name -> widget