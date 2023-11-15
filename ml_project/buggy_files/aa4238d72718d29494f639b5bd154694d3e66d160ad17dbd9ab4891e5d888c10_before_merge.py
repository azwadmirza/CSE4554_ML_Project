    def __init__(self):
        super(PhrasePage, self).__init__()
        self.setupUi(self)

        self.initialising = True
        l = list(model.SEND_MODES.keys())
        l.sort()
        for val in l:
            self.sendModeCombo.addItem(val)
        self.initialising = False