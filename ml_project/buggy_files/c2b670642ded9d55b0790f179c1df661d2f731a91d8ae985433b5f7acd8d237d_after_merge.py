    def __import(self, activator, library):
        cf = create_chooser_filter(_("Playlists"), ["*.pls", "*.m3u"])
        fns = choose_files(self, _("Import Playlist"), _("_Import"), cf)
        self._import_playlists(fns, library)