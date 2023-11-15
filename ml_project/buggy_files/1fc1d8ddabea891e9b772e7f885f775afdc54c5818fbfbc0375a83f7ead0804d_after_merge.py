    def _on_popup_menu(self, _widget: Gtk.Widget) -> bool:
        if self.Blueman is None:
            return False

        if self.menu is None:
            self.menu = ManagerDeviceMenu(self.Blueman)

        window = self.get_window()
        assert window is not None
        selected = self.selected()
        assert selected is not None
        rect = self.get_cell_area(self.liststore.get_path(selected), self.get_column(1))
        self.menu.popup_at_rect(window, rect, Gdk.Gravity.CENTER, Gdk.Gravity.NORTH)

        return True