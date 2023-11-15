def browse_file(parent, title):
    """Prompt user to select a single file"""

    if 'nt' == os.name and None == os.getenv('BB_NATIVE'):
        return Windows.browse_file(parent, title)

    chooser = Gtk.FileChooserDialog(title=title,
                                    transient_for=parent,
                                    action=Gtk.FileChooserAction.OPEN)
    chooser.add_buttons(_("_Cancel"), Gtk.ResponseType.CANCEL, _("_Open"), Gtk.ResponseType.OK)
    chooser.set_default_response(Gtk.ResponseType.OK)
    chooser.set_current_folder(expanduser('~'))
    resp = chooser.run()
    path = chooser.get_filename()
    chooser.destroy()

    if Gtk.ResponseType.OK != resp:
        # user cancelled
        return None

    return path