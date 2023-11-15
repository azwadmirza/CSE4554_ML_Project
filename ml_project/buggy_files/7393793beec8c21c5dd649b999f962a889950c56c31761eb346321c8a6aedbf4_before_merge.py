def selection_get_filenames(selection_data):
    """Extracts the filenames of songs set with selection_set_songs()
    from a Gtk.SelectionData.
    """

    data_type = selection_data.get_data_type()
    assert data_type.name() == "text/x-quodlibet-songs"

    items = selection_data.get_data().split("\x00")
    if sys.platform == "win32":
        return [item.decode("utf-8") for item in items]
    else:
        return items