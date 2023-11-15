    def __init__(self, width=WIDTH, height=HEIGHT):
        super(NcursesDisplay, self).__init__()
        self.dialog = dialog.Dialog()
        assert OK == self.dialog.DIALOG_OK, "What kind of absurdity is this?"
        self.width = width
        self.height = height