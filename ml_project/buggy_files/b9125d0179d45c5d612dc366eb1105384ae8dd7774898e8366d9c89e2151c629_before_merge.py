    def __init__(self, *args, **varargs):
        varargs["title"] = "Regular expression editor"
        super(RegexpDialog, self).__init__(*args, **varargs)
        self.__value = "Not initialized"
        self.__test_text = "Not initialized"
        self.__guesses = RE_FILENAME_GUESSES
        font = wx.Font(
            10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        self.font = font
        self.error_font = font

        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(hsizer, 0, wx.GROW | wx.ALL, 5)
        hsizer.Add(wx.StaticText(self, label="Regex:"), 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.regexp_display = wx.stc.StyledTextCtrl(self, -1, style=wx.BORDER_SIMPLE)
        self.regexp_display.SetBufferedDraw(True)
        o = self.regexp_display.GetFullTextExtent("".join(["M"] * 50))
        w, h = self.regexp_display.ClientToWindowSize(wx.Size(o[1], o[2]))
        self.regexp_display.SetMinSize(wx.Size(w, h))
        self.regexp_display.Text = self.value
        self.regexp_display.SetLexer(wx.stc.STC_LEX_CONTAINER)
        for key in range(31):
            self.regexp_display.StyleSetFont(key, self.font)
        self.regexp_display.StyleSetForeground(TOK_ORDINARY, wx.Colour(0, 0, 0, 255))
        self.regexp_display.StyleSetForeground(TOK_ESCAPE, wx.Colour(0, 64, 64, 255))
        self.regexp_display.StyleSetForeground(TOK_GROUP, wx.Colour(0, 0, 255, 255))
        self.regexp_display.StyleSetForeground(TOK_REPEAT, wx.Colour(0, 128, 0, 255))
        self.regexp_display.StyleSetForeground(
            TOK_BRACKET_EXP, wx.Colour(64, 64, 64, 255)
        )
        self.regexp_display.StyleSetForeground(TOK_SPECIAL, wx.Colour(128, 64, 0, 255))
        color_db = self.get_color_db()
        for i in range(1, 16):
            self.regexp_display.StyleSetForeground(
                TOK_DEFINITION - 1 + i, color_db[i % len(color_db)]
            )

        self.regexp_display.StyleSetForeground(
            STYLE_ERROR, wx.Colour(255, 64, 128, 255)
        )
        self.regexp_display.StyleSetFont(34, self.font)
        self.regexp_display.StyleSetForeground(34, wx.Colour(0, 0, 255, 255))
        self.regexp_display.StyleSetUnderline(34, True)
        self.regexp_display.StyleSetFont(35, self.font)
        self.regexp_display.StyleSetForeground(35, wx.Colour(255, 0, 0, 255))
        self.regexp_display.SetUseVerticalScrollBar(0)
        self.regexp_display.SetUseHorizontalScrollBar(0)
        self.regexp_display.SetMarginWidth(wx.stc.STC_MARGIN_NUMBER, 0)
        self.regexp_display.SetMarginWidth(wx.stc.STC_MARGIN_SYMBOL, 0)
        hsizer.Add(self.regexp_display, 1, wx.EXPAND | wx.ALL, 5)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(
            wx.StaticText(self, label="Test text:"), 0, wx.ALIGN_CENTER | wx.ALL, 5
        )
        self.test_text_ctl = wx.TextCtrl(self, value=self.__test_text)
        self.test_text_ctl.Font = self.font
        hsizer.Add(self.test_text_ctl, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(hsizer, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        style = wx.NO_BORDER
        self.test_display = wx.stc.StyledTextCtrl(self, -1, style=style)
        self.test_display.SetLexer(wx.stc.STC_LEX_CONTAINER)
        self.test_display.StyleClearAll()
        self.test_display.StyleSetFont(STYLE_NO_MATCH, self.font)
        self.test_display.StyleSetForeground(
            STYLE_NO_MATCH, wx.Colour(128, 128, 128, 255)
        )
        color_db = self.get_color_db()
        for i in range(16):
            self.test_display.StyleSetFont(STYLE_FIRST_LABEL - 1 + i, self.font)
            self.test_display.StyleSetForeground(
                STYLE_FIRST_LABEL - 1 + i, color_db[i % len(color_db)]
            )

        self.test_display.StyleSetFont(STYLE_ERROR, self.error_font)
        self.test_display.StyleSetForeground(STYLE_ERROR, wx.Colour(255, 0, 0, 255))
        self.test_display.Text = self.__test_text
        self.test_display.SetReadOnly(True)
        self.test_display.SetUseVerticalScrollBar(0)
        self.test_display.SetUseHorizontalScrollBar(0)
        self.test_display.SetMarginWidth(wx.stc.STC_MARGIN_NUMBER, 0)
        self.test_display.SetMarginWidth(wx.stc.STC_MARGIN_SYMBOL, 0)
        text_extent = self.test_display.GetFullTextExtent(self.__test_text)
        self.test_display.SetSizeHints(100, text_extent[1] + 3, maxH=text_extent[1] + 3)
        self.test_display.Enable(False)
        sizer.Add(self.test_display, 0, wx.EXPAND | wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW | wx.RIGHT | wx.LEFT, 5)

        hsizer = wx.StdDialogButtonSizer()
        guess_button = wx.Button(self, label="Guess")
        hsizer.Add(guess_button, 0)
        ok_button = wx.Button(self, label="Submit")
        ok_button.SetDefault()
        hsizer.Add(ok_button, 0, wx.LEFT, 5)
        cancel_button = wx.Button(self, label="Cancel")
        hsizer.Add(cancel_button, 0, wx.LEFT, 5)
        hsizer.Realize()
        sizer.Add(hsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self.on_guess, guess_button)
        self.Bind(wx.EVT_BUTTON, self.on_ok_button, ok_button)
        self.Bind(wx.EVT_BUTTON, self.on_cancel_button, cancel_button)
        self.Bind(wx.EVT_TEXT, self.on_test_text_text_change, self.test_text_ctl)
        self.Bind(
            wx.stc.EVT_STC_CHANGE, self.on_editor_text_change, self.regexp_display
        )
        self.Bind(wx.stc.EVT_STC_STYLENEEDED, self.on_style_needed, self.regexp_display)
        self.regexp_display.Bind(wx.EVT_KEY_DOWN, self.on_regexp_key)
        self.SetSizer(sizer)
        self.Fit()