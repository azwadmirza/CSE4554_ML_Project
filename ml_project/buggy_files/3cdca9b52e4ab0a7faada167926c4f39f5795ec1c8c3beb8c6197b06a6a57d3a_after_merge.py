    def copy(self):
        return DownloadConfigInterface(dlconfig=self.dlconfig.copy(), state_dir=self.state_dir)