def selection_set_songs(selection_data, songs):
    """Stores filenames of the passed songs in a Gtk.SelectionData"""

    filenames = []
    for filename in (song["~filename"] for song in songs):
        filenames.append(fsn2bytes(filename, "utf-8"))
    type_ = Gdk.atom_intern("text/x-quodlibet-songs", True)
    selection_data.set(type_, 8, b"\x00".join(filenames))