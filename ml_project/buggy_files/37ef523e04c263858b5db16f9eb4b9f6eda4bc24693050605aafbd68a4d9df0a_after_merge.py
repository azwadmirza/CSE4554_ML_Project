    def __drag_data_received(self, view, ctx, x, y, sel, info, etime, library):
        model = view.get_model()
        if info == DND_QL:
            filenames = qltk.selection_get_filenames(sel)
            move = bool(ctx.get_selected_action() & Gdk.DragAction.MOVE)
        elif info == DND_URI_LIST:
            def to_filename(s):
                try:
                    return uri2fsn(s)
                except ValueError:
                    return None

            filenames = listfilter(None, map(to_filename, sel.get_uris()))
            move = False
        else:
            Gtk.drag_finish(ctx, False, False, etime)
            return

        to_add = []
        for filename in filenames:
            if filename not in library.librarian:
                library.add_filename(filename)
            elif filename not in library:
                to_add.append(library.librarian[filename])
        library.add(to_add)
        songs = listfilter(None, map(library.get, filenames))
        if not songs:
            Gtk.drag_finish(ctx, bool(not filenames), False, etime)
            return

        if not self.__drop_by_row:
            success = self.__drag_data_browser_dropped(songs)
            Gtk.drag_finish(ctx, success, False, etime)
            return

        try:
            path, position = view.get_dest_row_at_pos(x, y)
        except TypeError:
            path = max(0, len(model) - 1)
            position = Gtk.TreeViewDropPosition.AFTER

        if move and Gtk.drag_get_source_widget(ctx) == view:
            iter = model.get_iter(path) # model can't be empty, we're moving
            if position in (Gtk.TreeViewDropPosition.BEFORE,
                            Gtk.TreeViewDropPosition.INTO_OR_BEFORE):
                while self.__drag_iters:
                    model.move_before(self.__drag_iters.pop(0), iter)
            else:
                while self.__drag_iters:
                    model.move_after(self.__drag_iters.pop(), iter)
            Gtk.drag_finish(ctx, True, False, etime)
        else:
            song = songs.pop(0)
            try:
                iter = model.get_iter(path)
            except ValueError:
                iter = model.append(row=[song]) # empty model
            else:
                if position in (Gtk.TreeViewDropPosition.BEFORE,
                                Gtk.TreeViewDropPosition.INTO_OR_BEFORE):
                    iter = model.insert_before(iter, [song])
                else:
                    iter = model.insert_after(iter, [song])
            for song in songs:
                iter = model.insert_after(iter, [song])
            Gtk.drag_finish(ctx, True, move, etime)