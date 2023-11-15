    def save(self):
        self.settingsWidget.save()
        self.currentPhrase.phrase = str(self.phraseText.toPlainText())
        self.currentPhrase.show_in_tray_menu = self.showInTrayCheckbox.isChecked()

        self.currentPhrase.sendMode = model.SEND_MODES[str(self.sendModeCombo.currentText())]

        # TODO - re-enable me if restoring predictive functionality
        #if self.predictCheckbox.isChecked():
        #    self.currentPhrase.modes.append(model.TriggerMode.PREDICTIVE)

        self.currentPhrase.prompt = self.promptCheckbox.isChecked()

        self.currentPhrase.persist()
        ui_common.set_url_label(self.urlLabel, self.currentPhrase.path)
        return False