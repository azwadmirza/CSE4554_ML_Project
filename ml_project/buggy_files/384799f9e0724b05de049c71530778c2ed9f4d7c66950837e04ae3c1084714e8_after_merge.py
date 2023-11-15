    def on_item_clicked(self, item):
        item_ind = self.row(item)
        if self.loaded_list:
            self.playing_item_change.emit(item_ind)