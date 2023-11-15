    def _show_context_menu(self, pos):
        if not self.table_view:
            return

        item_index = self.table_view.indexAt(pos)
        if not item_index or item_index.row() < 0:
            return

        menu = TriblerActionMenu(self.table_view)

        # Single selection menu items
        num_selected = len(self.table_view.selectionModel().selectedRows())
        if num_selected == 1:
            self.add_menu_item(menu, ' Download ', item_index, self.table_view.on_download_button_clicked)
            self.add_menu_item(menu, ' Play ', item_index, self.table_view.on_play_button_clicked)

        if not isinstance(self, MyTorrentsTableViewController):
            if self.selection_has_torrents():
                self.add_menu_item(menu, ' Add to My Channel ', item_index,
                                   self.table_view.on_add_to_channel_button_clicked)
        else:
            self.add_menu_item(menu, ' Remove from My Channel ', item_index, self.table_view.on_delete_button_clicked)

        menu.exec_(QCursor.pos())