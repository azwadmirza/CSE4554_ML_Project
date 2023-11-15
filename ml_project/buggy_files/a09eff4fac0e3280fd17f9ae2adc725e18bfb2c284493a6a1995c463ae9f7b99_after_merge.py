    def convert_on_import(self, lib, item):
        """Transcode a file automatically after it is imported into the
        library.
        """
        fmt = self.config['format'].get(unicode).lower()
        if should_transcode(item, fmt):
            command, ext = get_format()
            fd, dest = tempfile.mkstemp('.' + ext)
            os.close(fd)
            _temp_files.append(dest)  # Delete the transcode later.
            try:
                self.encode(command, item.path, dest)
            except subprocess.CalledProcessError:
                return
            item.path = dest
            item.write()
            item.read()  # Load new audio information data.
            item.store()