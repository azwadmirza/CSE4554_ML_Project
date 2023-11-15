def browse_files(parent, title):
    """Prompt user to select multiple files to delete"""

    if 'nt' == os.name and None == os.getenv('BB_NATIVE'):
        return Windows.browse_files(parent.window.handle, title)

    chooser = Gtk.FileChooserDialog(title=title,
                                    transient_for=parent,
                                    action=Gtk.FileChooserAction.OPEN)
    chooser.add_buttons(_("_Cancel"), Gtk.ResponseType.CANCEL, _("_Delete"), Gtk.ResponseType.OK)
    chooser.set_default_response(Gtk.ResponseType.OK)
    chooser.set_select_multiple(True)
    chooser.set_current_folder(expanduser('~'))
    resp = chooser.run()
    paths = chooser.get_filenames()
    chooser.destroy()

    if Gtk.ResponseType.OK != resp:
        # user cancelled
        return None

    return paths