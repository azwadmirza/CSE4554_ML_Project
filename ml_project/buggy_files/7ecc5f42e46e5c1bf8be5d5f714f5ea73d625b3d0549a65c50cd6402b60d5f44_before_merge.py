    def start(self, workspace_folder):
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler, workspace_folder, recursive=True)
        self.observer.start()