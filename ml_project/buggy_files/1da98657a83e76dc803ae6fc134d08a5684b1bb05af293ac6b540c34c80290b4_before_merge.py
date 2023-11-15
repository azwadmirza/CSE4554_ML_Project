    def __drag_data_received(self, view, ctx, x, y, sel, tid, etime, library):
        # TreeModelSort doesn't support GtkTreeDragDestDrop.
        view.emit_stop_by_name('drag-data-received')
        model = view.get_model()
        if tid == DND_QL:
            filenames = qltk.selection_get_filenames(sel)
            songs = listfilter(None, [library.get(f) for f in filenames])
            if not songs:
                Gtk.drag_finish(ctx, False, False, etime)
                return
            try:
                path, pos = view.get_dest_row_at_pos(x, y)
            except TypeError:
                playlist = FileBackedPlaylist.from_songs(PLAYLISTS, songs,
                                                         library)
                GLib.idle_add(self._select_playlist, playlist)
            else:
                playlist = model[path][0]
                playlist.extend(songs)
            self.changed(playlist)
            Gtk.drag_finish(ctx, True, False, etime)
        else:
            if tid == DND_URI_LIST:
                uri = sel.get_uris()[0]
                name = os.path.basename(uri)
            elif tid == DND_MOZ_URL:
                data = sel.get_data()
                uri, name = data.decode('utf16', 'replace').split('\n')
            else:
                Gtk.drag_finish(ctx, False, False, etime)
                return
            name = _name_for(name or os.path.basename(uri))
            uri = uri.encode('utf-8')
            try:
                sock = urlopen(uri)
                f = NamedTemporaryFile()
                f.write(sock.read())
                f.flush()
                if uri.lower().endswith('.pls'):
                    playlist = parse_pls(f.name, library=library)
                elif uri.lower().endswith('.m3u'):
                    playlist = parse_m3u(f.name, library=library)
                else:
                    raise IOError
                library.add(playlist.songs)
                if name:
                    playlist.rename(name)
                self.changed(playlist)
                Gtk.drag_finish(ctx, True, False, etime)
            except IOError:
                Gtk.drag_finish(ctx, False, False, etime)
                qltk.ErrorMessage(
                    qltk.get_top_parent(self),
                    _("Unable to import playlist"),
                    _("Quod Libet can only import playlists in the M3U "
                      "and PLS formats.")).run()