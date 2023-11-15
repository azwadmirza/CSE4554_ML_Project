    def _save_lang(self):
        """
        Get selected language setting and save to language configuration file.
        """
        for combobox, (option, _default) in list(self.comboboxes.items()):
            if option == 'interface_language':
                data = combobox.itemData(combobox.currentIndex())
                value = from_qvariant(data, to_text_string)
                break
        try:
            save_lang_conf(value)
            self.set_option('interface_language', value)
        except Exception:
            QMessageBox.critical(self, _("Error"),
                _("We're sorry but the following error occurred while trying "
                  "to set your selected language:<br><br>"
                  "<tt>{}</tt>").format(traceback.format_exc()),
                QMessageBox.Ok)
            return