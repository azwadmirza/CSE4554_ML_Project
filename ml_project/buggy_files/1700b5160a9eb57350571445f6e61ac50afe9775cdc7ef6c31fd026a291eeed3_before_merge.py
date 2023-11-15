    def save_to_conf(self):
        """Save settings to configuration file"""
        for checkbox, (option, _default) in list(self.checkboxes.items()):
            self.set_option(option, checkbox.isChecked())
        for radiobutton, (option, _default) in list(self.radiobuttons.items()):
            self.set_option(option, radiobutton.isChecked())
        for lineedit, (option, _default) in list(self.lineedits.items()):
            data = lineedit.text()
            if lineedit.content_type == list:
                data = [item.strip() for item in data.split(',')]
            else:
                data = to_text_string(data)
            self.set_option(option, data)
        for textedit, (option, _default) in list(self.textedits.items()):
            data = textedit.toPlainText()
            if textedit.content_type == dict:
                if data:
                    data = ast.literal_eval(data)
                else:
                    data = textedit.content_type()
            elif textedit.content_type in (tuple, list):
                data = [item.strip() for item in data.split(',')]
            else:
                data = to_text_string(data)
            self.set_option(option, data)
        for spinbox, (option, _default) in list(self.spinboxes.items()):
            self.set_option(option, spinbox.value())
        for combobox, (option, _default) in list(self.comboboxes.items()):
            data = combobox.itemData(combobox.currentIndex())
            self.set_option(option, from_qvariant(data, to_text_string))
        for (fontbox, sizebox), option in list(self.fontboxes.items()):
            font = fontbox.currentFont()
            font.setPointSize(sizebox.value())
            self.set_font(font, option)
        for clayout, (option, _default) in list(self.coloredits.items()):
            self.set_option(option, to_text_string(clayout.lineedit.text()))
        for (clayout, cb_bold, cb_italic), (option, _default) in list(self.scedits.items()):
            color = to_text_string(clayout.lineedit.text())
            bold = cb_bold.isChecked()
            italic = cb_italic.isChecked()
            self.set_option(option, (color, bold, italic))