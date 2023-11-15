    def set_dest_dir(self, new_dir):
        new_dir = new_dir

        new_dir = os.path.expanduser(new_dir)
        if os.path.isdir(new_dir):
            self.destination_dir = new_dir
        else:
            logger.warning('"{}" is not a directory'.format(new_dir))
            return

        self.exports = []
        self.add_exports()
        self._update_ui()