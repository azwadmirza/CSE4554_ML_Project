    def init_ui(self):
        self.add_menu()
        self.menu.label = 'Batch Export Recordings'

        self.menu.append(ui.Info_Text('Search will walk through the source direcotry recursively and detect available Pupil recordings.'))
        self.menu.append(ui.Text_Input('source_dir', self, label='Source directory', setter=self.set_src_dir))

        self.search_button = ui.Button('Search', self.detect_recordings)
        self.menu.append(self.search_button)

        self.avail_recs_menu = ui.Growing_Menu('Available Recordings')
        self._update_avail_recs_menu()
        self.menu.append(self.avail_recs_menu)

        self.menu.append(ui.Text_Input('destination_dir', self, label='Destination directory', setter=self.set_dest_dir))
        self.menu.append(ui.Button('Export selected', self.queue_selected))
        self.menu.append(ui.Button('Clear search results', self._clear_avail))
        self.menu.append(ui.Separator())
        self.menu.append(ui.Button('Cancel all exports', self.cancel_all))