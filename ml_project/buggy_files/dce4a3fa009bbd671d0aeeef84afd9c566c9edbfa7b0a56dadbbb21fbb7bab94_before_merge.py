    def __init__(self, win, text, font,
                 pos=(0, 0), units=None, letterHeight=None,
                 size=None,
                 color=(1.0, 1.0, 1.0), colorSpace='rgb',
                 fillColor=None, fillColorSpace=None,
                 borderWidth=2, borderColor=None, borderColorSpace=None,
                 contrast=1,
                 opacity=1.0,
                 bold=False,
                 italic=False,
                 lineSpacing=1.0,
                 padding=None,  # gap between box and text
                 anchor='center',
                 alignment='left',
                 flipHoriz=False,
                 flipVert=False,
                 editable=False,
                 name='',
                 autoLog=None,
                 onTextCallback=None):
        """

        Parameters
        ----------
        win
        text
        font
        pos
        units
        letterHeight
        size : Specifying None gets the default size for this type of unit.
            Specifying [None, None] gets a TextBox that's expandable in both
            dimensions. Specifying [0.75, None] gets a textbox that expands in the
            length but fixed at 0.75 units in the width
        color
        colorSpace
        contrast
        opacity
        bold
        italic
        lineSpacing
        padding
        anchor
        alignment
        fillColor
        borderWidth
        borderColor
        flipHoriz
        flipVert
        editable
        name
        autoLog
        """

        BaseVisualStim.__init__(self, win, units=units, name=name)
        self.win = win
        self.colorSpace = colorSpace
        self.color = color
        self.contrast = contrast
        self.opacity = opacity
        self.onTextCallback = onTextCallback

        if units=='norm':
            raise NotImplemented("TextBox2 doesn't support 'norm' units at the "
                                 "moment. Use 'height' units instead")
        # first set params needed to create font (letter sizes etc)
        if letterHeight is None:
            self.letterHeight = defaultLetterHeight[self.units]
        else:
            self.letterHeight = letterHeight
        # self._pixLetterHeight helps get font size right but not final layout
        if 'deg' in self.units:  # treat deg, degFlat or degFlatPos the same
            scaleUnits = 'deg'  # scale units are just for font resolution
        else:
            scaleUnits = self.units
        self._pixLetterHeight = convertToPix(
                self.letterHeight, pos=0, units=scaleUnits, win=self.win)
        if isinstance(self._pixLetterHeight, np.ndarray):
            # If pixLetterHeight is an array, take the Height value
            self._pixLetterHeight = self._pixLetterHeight[1]
        self._pixelScaling = self._pixLetterHeight / self.letterHeight
        if size is None:
            size = [defaultBoxWidth[self.units], None]
        self.size = size  # but this will be updated later to actual size
        self.bold = bold
        self.italic = italic
        self.lineSpacing = lineSpacing
        if padding is None:
            padding = self.letterHeight / 2.0
        self.padding = padding
        self.glFont = None  # will be set by the self.font attribute setter
        self.font = font

        # once font is set up we can set the shader (depends on rgb/a of font)
        if self.glFont.atlas.format == 'rgb':
            global rgbShader
            self.shader = rgbShader = shaders.Shader(
                    shaders.vertSimple, shaders.fragTextBox2)
        else:
            global alphaShader
            self.shader = alphaShader = shaders.Shader(
                    shaders.vertSimple, shaders.fragTextBox2alpha)
        self._needVertexUpdate = False  # this will be set True during layout

        # standard stimulus params
        self.pos = pos
        self.ori = 0.0
        self.depth = 0.0
        # used at render time
        self._lines = None  # np.array the line numbers for each char
        self._colors = None
        self.flipHoriz = flipHoriz
        self.flipVert = flipVert
        # params about positioning (after layout has occurred)
        self.anchor = anchor  # 'center', 'top_left', 'bottom-center'...
        self.alignment = alignment

        # box border and fill
        w, h = self.size
        self.borderWidth = borderWidth
        self.borderColor = borderColor
        self.fillColor = fillColor

        self.box = Rect(
                win, pos=self.pos,
                units=self.units,
                lineWidth=borderWidth, lineColor=borderColor,
                fillColor=fillColor, opacity=self.opacity,
                autoLog=False, fillColorSpace=self.colorSpace)
        # also bounding box (not normally drawn but gives tight box around chrs)
        self.boundingBox = Rect(
                win, pos=self.pos,
                units=self.units,
                lineWidth=1, lineColor=None, fillColor=fillColor, opacity=0.1,
                autoLog=False)
        # then layout the text (setting text triggers _layout())
        self.startText = text
        self.text = text if text is not None else ""

        # caret
        self.editable = editable
        self.caret = Caret(self, color=self.color, width=5)
        self._hasFocus = False

        self.autoLog = autoLog