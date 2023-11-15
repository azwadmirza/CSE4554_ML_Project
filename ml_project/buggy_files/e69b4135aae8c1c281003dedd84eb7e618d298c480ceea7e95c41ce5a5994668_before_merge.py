def selection_set_songs(selection_data, songs):
    """Stores filenames of the passed songs in a Gtk.SelectionData"""

    filenames = []
    for filename in (song["~filename"] for song in songs):
        if isinstance(filename, text_type):
            # win32
            filename = filename.encode("utf-8")
        filenames.append(filename)

    type_ = Gdk.atom_intern("text/x-quodlibet-songs", True)
    selection_data.set(type_, 8, "\x00".join(filenames))