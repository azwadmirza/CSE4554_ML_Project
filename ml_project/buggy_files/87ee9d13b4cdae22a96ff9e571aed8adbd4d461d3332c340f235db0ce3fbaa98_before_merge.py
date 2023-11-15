    def received_popular_channels(self, result):
        self.show_channels = True
        if not self.has_loaded_cells:
            self.load_cells()

        if len(result["channels"]) == 0:
            self.set_no_results_table(label_text="No recommended channels")
            return

        cur_ind = 0
        for channel in result["channels"][:9]:
            self.window().home_page_table_view.cellWidget(cur_ind % 3, cur_ind / 3).update_with_channel(channel)
            cur_ind += 1

        self.window().resizeEvent(None)