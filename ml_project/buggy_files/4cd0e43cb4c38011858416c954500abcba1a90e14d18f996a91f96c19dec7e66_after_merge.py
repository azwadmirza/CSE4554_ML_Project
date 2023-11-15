    def save(self):
        self.settingsWidget.save()
        self.current_phrase.phrase = str(self.phraseText.toPlainText())
        self.current_phrase.show_in_tray_menu = self.showInTrayCheckbox.isChecked()

        self.current_phrase.sendMode = model.SEND_MODES[str(self.sendModeCombo.currentText())]

        # TODO - re-enable me if restoring predictive functionality
        #if self.predictCheckbox.isChecked():
        #    self.currentPhrase.modes.append(model.TriggerMode.PREDICTIVE)

        self.current_phrase.prompt = self.promptCheckbox.isChecked()

        self.current_phrase.persist()
        ui_common.set_url_label(self.urlLabel, self.current_phrase.path)
        return False