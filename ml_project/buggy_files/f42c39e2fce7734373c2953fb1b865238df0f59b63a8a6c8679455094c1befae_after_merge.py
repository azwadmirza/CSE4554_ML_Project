    def received_popular_torrents(self, result):
        if not result:
            return
        self.show_channels = False
        if not self.has_loaded_cells:
            self.load_cells()

        if len(result["torrents"]) == 0:
            self.set_no_results_table(label_text="No recommended torrents")
            return

        cur_ind = 0
        for torrent in result["torrents"][:9]:
            self.window().home_page_table_view.cellWidget(cur_ind % 3, cur_ind / 3).update_with_torrent(torrent)
            cur_ind += 1

        self.window().resizeEvent(None)