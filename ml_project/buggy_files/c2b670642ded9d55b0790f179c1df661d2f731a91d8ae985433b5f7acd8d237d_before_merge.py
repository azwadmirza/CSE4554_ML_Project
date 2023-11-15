    def __import(self, activator, library):
        cf = create_chooser_filter(_("Playlists"), ["*.pls", "*.m3u"])
        fns = choose_files(self, _("Import Playlist"), _("_Import"), cf)
        for filename in fns:
            if filename.endswith(".m3u"):
                playlist = parse_m3u(filename, library=library)
            elif filename.endswith(".pls"):
                playlist = parse_pls(filename, library=library)
            else:
                continue
            self.changed(playlist)
            library.add(playlist)