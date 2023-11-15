    def open_switcher_dlg(self, initial_text=''):
        """Open file list management dialog box"""
        if not self.tabs.count():
            return
        if self.switcher_dlg is not None and self.switcher_dlg.isVisible():
            self.switcher_dlg.hide()
            self.switcher_dlg.clear()
            return
        if self.switcher_dlg is None:
            from spyder.widgets.switcher import Switcher
            self.switcher_dlg = Switcher(self)
            self.switcher_manager = EditorSwitcherManager(
                self.switcher_dlg,
                lambda: self.get_current_editor(),
                lambda: self,
                section=self.get_plugin_title())

        self.switcher_dlg.set_search_text(initial_text)
        self.switcher_dlg.setup()
        self.switcher_dlg.show()
        # Note: the +1 pixel on the top makes it look better
        delta_top = (self.tabs.tabBar().geometry().height() +
                     self.fname_label.geometry().height() + 1)
        self.switcher_dlg.set_position(delta_top)