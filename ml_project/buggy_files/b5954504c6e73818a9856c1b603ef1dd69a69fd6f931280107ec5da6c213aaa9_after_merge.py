    def move_storage(self, new_dir):
        if not isinstance(self.tdef, TorrentDefNoMetainfo):
            self.handle.move_storage(str(new_dir))
        self.config.set_dest_dir(new_dir)