    def load(self):
        """
        Load a config file from the list of paths, if it exists
        """
        for path in self.get_paths_list():
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                try:
                    if is_PY3:
                        self.parser.read(path, encoding='utf-8')
                    else:
                        self.parser.read(path)
                except UnicodeDecodeError as e:
                    print(_("Error decoding config file '%s': %s") % (path, e))
                    sys.exit(1)

                break