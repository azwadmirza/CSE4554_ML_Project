    def add_directory(self, path):
        """Add ``*.py`` files under the directory ``path`` to the archive.
        """
        for root, dirs, files in os.walk(path):
            arc_prefix = os.path.relpath(root, os.path.dirname(path))
            for f in files:
                if f.endswith('.pyc') or f.endswith('.c'):
                    continue
                f_path = os.path.join(root, f)
                dest_path = os.path.join(arc_prefix, f)
                self.add_file(f_path, dest_path)