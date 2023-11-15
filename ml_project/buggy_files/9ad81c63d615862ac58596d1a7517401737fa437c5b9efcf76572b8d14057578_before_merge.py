    def on_torrents_remove_selected_clicked(self):
        num_selected = len(self.window().edit_channel_torrents_list.selectedItems())
        if num_selected == 0:
            return

        item = self.window().edit_channel_torrents_list.itemWidget(
            self.window().edit_channel_torrents_list.selectedItems()[0])

        self.dialog = ConfirmationDialog(self, "Remove %s selected torrents" % num_selected,
                                         "Are you sure that you want to remove %s selected torrents "
                                         "from your channel?" % num_selected,
                                         [('CONFIRM', BUTTON_TYPE_NORMAL), ('CANCEL', BUTTON_TYPE_CONFIRM)])
        self.dialog.button_clicked.connect(lambda action: self.on_torrents_remove_selected_action(action, item))
        self.dialog.show()