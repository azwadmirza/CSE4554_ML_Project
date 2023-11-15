    def __init__(self):
        super(PhrasePage, self).__init__()
        self.setupUi(self)

        self.initialising = True
        self.current_phrase = None  # type: model.Phrase

        for val in sorted(model.SEND_MODES.keys()):
            self.sendModeCombo.addItem(val)
        self.initialising = False