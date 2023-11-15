    def set_src_dir(self, new_dir):
        new_dir = new_dir
        self.new_exports = []
        self.exports = []
        new_dir = os.path.expanduser(new_dir)
        if os.path.isdir(new_dir):
            self.source_dir = new_dir
            self.new_exports = get_recording_dirs(new_dir)
        else:
            logger.warning('"{}" is not a directory'.format(new_dir))
            return
        if self.new_exports is []:
            logger.warning('"{}" does not contain recordings'.format(new_dir))
            return

        self.add_exports()
        self._update_ui()