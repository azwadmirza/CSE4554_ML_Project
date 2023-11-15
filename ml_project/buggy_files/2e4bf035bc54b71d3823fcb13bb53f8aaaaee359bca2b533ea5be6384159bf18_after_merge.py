    def set_src_dir(self, new_dir):
        new_dir = os.path.expanduser(new_dir)
        if os.path.isdir(new_dir):
            self.source_dir = new_dir
        else:
            logger.warning('"{}" is not a directory'.format(new_dir))
            return