    def on_show_error(self, widget, data=None):
        self.app.show_script_error(self.app.configWindow.ui)
        self.errorItem.hide()
        self.update_visible_status()