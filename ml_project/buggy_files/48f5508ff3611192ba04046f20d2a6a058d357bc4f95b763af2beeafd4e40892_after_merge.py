    def __init__(self, textbox, color, width, colorSpace='rgb'):
        self.textbox = textbox
        self.index = len(textbox._layoutText)  # start off at the end
        self.autoLog = False
        self.width = width
        self.units = textbox.units
        self.colorSpace = colorSpace
        self.color = color