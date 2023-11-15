def select_file(strings, filename=None):
    # get filename, either from argument or file chooser dialog
    if not filename:
        args = {}
        if onionshare.get_platform() == 'Tails':
            args['directory'] = '/home/amnesia'

        filename = QFileDialog.getOpenFileName(caption=translated('choose_file'), options=QFileDialog.ReadOnly, **args)
        if not filename:
            return False, False

        filename = str(unicode(filename).encode("utf-8"))

    # validate filename
    if not os.path.isfile(filename):
        alert(translated("not_a_file").format(filename), QMessageBox.Warning)
        return False, False

    filename = os.path.abspath(filename)
    basename = os.path.basename(filename)
    return filename, basename