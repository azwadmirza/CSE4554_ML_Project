    def setup_drag_n_drop(self):
        def cb_drag_data_received(widget, context, x, y, data, info, time):
            if info == 80:
                uris = data.get_uris()
                paths = FileUtilities.uris_to_paths(uris)
                self.shred_paths(paths)

        self.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.HIGHLIGHT | Gtk.DestDefaults.DROP,
                           [Gtk.TargetEntry.new("text/uri-list", 0, 80)], Gdk.DragAction.COPY)
        self.connect('drag_data_received', cb_drag_data_received)