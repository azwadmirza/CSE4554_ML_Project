def browse_folder(parent, title, multiple, stock_button):
    """Ask the user to select a folder.  Return the full path or None."""

    if 'nt' == os.name and None == os.getenv('BB_NATIVE'):
        ret = Windows.browse_folder(parent, title)
        return [ret] if multiple and not ret is None else ret

    # fall back to GTK+
    chooser = Gtk.FileChooserDialog(transient_for=parent,
                                    title=title,
                                    action = Gtk.FileChooserAction.SELECT_FOLDER)
    chooser.add_buttons(_("_Cancel"), Gtk.ResponseType.CANCEL, stock_button, Gtk.ResponseType.OK)
    chooser.set_default_response(Gtk.ResponseType.OK)
    chooser.set_select_multiple(multiple)
    chooser.set_current_folder(expanduser('~'))
    resp = chooser.run()
    if multiple:
        ret = chooser.get_filenames()
    else:
        ret = chooser.get_filename()
    chooser.hide()
    chooser.destroy()
    if Gtk.ResponseType.OK != resp:
        # user cancelled
        return None
    return ret