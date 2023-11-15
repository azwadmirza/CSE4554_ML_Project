    def on_torrents_remove_selected_clicked(self):
        num_selected = len(self.window().edit_channel_torrents_list.selectedItems())
        if num_selected == 0:
            return

        selected_torrent_items = [self.window().edit_channel_torrents_list.itemWidget(list_widget_item)
                                  for list_widget_item in self.window().edit_channel_torrents_list.selectedItems()]

        self.dialog = ConfirmationDialog(self, "Remove %s selected torrents" % num_selected,
                                         "Are you sure that you want to remove %s selected torrents "
                                         "from your channel?" % num_selected,
                                         [('CONFIRM', BUTTON_TYPE_NORMAL), ('CANCEL', BUTTON_TYPE_CONFIRM)])
        self.dialog.button_clicked.connect(lambda action:
                                           self.on_torrents_remove_selected_action(action, selected_torrent_items))
        self.dialog.show()