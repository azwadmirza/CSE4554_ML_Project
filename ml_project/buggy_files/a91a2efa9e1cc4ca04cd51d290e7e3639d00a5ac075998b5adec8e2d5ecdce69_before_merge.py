    def refresh_plugin(self):
        """Refresh tabwidget"""
        client = None
        if self.tabwidget.count():
            # Give focus to the control widget of the selected tab
            client = self.tabwidget.currentWidget()
            control = client.get_control()
            control.setFocus()
            widgets = client.get_toolbar_buttons()+[5]
        else:
            control = None
            widgets = []
        self.find_widget.set_editor(control)
        self.tabwidget.set_corner_widgets({Qt.TopRightCorner: widgets})
        if client:
            sw = client.shellwidget
            self.variableexplorer.set_shellwidget_from_id(id(sw))
            self.help.set_shell(sw)
        self.main.last_console_plugin_focus_was_python = False
        self.sig_update_plugin_title.emit()