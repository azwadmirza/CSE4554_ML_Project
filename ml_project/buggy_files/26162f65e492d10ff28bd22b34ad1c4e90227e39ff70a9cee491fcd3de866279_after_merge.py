    def on_received_files(self, files):
        if not files:
            return
        if "files" not in files or not files["files"]:
            return

        if self.files_request_timer:
            self.files_request_timer.stop()
            self.files_request_timer = None

        self.set_files(files["files"])
        self.loaded_list = True
        self.loading_list = False
        self.list_loaded.emit()