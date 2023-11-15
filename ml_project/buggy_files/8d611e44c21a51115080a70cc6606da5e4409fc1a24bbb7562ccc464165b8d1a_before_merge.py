    def refresh_text(self):
        self.test_display.SetReadOnly(False)
        self.test_display.Text = self.__test_text
        try:
            parse(self.__value, RegexpState())
        except ValueError as e:
            self.test_display.Text = e.args[0]
            self.test_display.StartStyling(0, 0xFF)
            self.test_display.SetStyling(len(self.test_display.Text), STYLE_ERROR)
            return
        try:
            match = re.search(self.__value, self.__test_text)
            if match:
                for i in range(len(match.groups()) + 1):
                    start = match.start(i)
                    end = match.end(i)
                    self.test_display.StartStyling(start, 0xFF)
                    self.test_display.SetStyling(end - start, i + 1)
            else:
                self.test_display.Text = "Regular expression does not match"
                self.test_display.StartStyling(0, 0xFF)
                self.test_display.SetStyling(len(self.test_display.Text), STYLE_ERROR)
        except:
            self.test_display.Text = "Regular expression is not valid"
            self.test_display.StartStyling(0, 0xFF)
            self.test_display.SetStyling(len(self.test_display.GetText()), STYLE_ERROR)
        self.test_display.SetReadOnly(True)