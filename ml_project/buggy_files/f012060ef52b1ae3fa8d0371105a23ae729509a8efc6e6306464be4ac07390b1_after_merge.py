    def refresh_regexp(self):
        state = RegexpState()
        regexp_text = self.__value
        self.regexp_display.StartStyling(0)
        self.regexp_display.SetStyling(len(regexp_text), STYLE_ERROR)
        try:
            parse(regexp_text, state)
        except:
            pass
        for i in range(state.position):
            self.regexp_display.StartStyling(i)
            self.regexp_display.SetStyling(1, state.token_labels[i])
        pos = self.regexp_display.CurrentPos
        if state.open_expression_start is not None:
            self.regexp_display.BraceBadLight(state.open_expression_start)
        elif (
            0 < pos < len(state.matching_braces)
            and state.matching_braces[pos - 1] is not None
        ):
            self.regexp_display.BraceHighlight(state.matching_braces[pos - 1], pos - 1)
        else:
            self.regexp_display.BraceHighlight(
                wx.stc.STC_INVALID_POSITION, wx.stc.STC_INVALID_POSITION
            )