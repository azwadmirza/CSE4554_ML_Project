def save_svg(string, parent=None):
    """ Prompts the user to save an SVG document to disk.

    Parameters:
    -----------
    string : basestring
        A Python string containing a SVG document.

    parent : QWidget, optional
        The parent to use for the file dialog.

    Returns:
    --------
    The name of the file to which the document was saved, or None if the save
    was cancelled.
    """
    if isinstance(string, unicode):
        string = string.encode('utf-8')

    dialog = QtGui.QFileDialog(parent, 'Save SVG Document')
    dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
    dialog.setDefaultSuffix('svg')
    dialog.setNameFilter('SVG document (*.svg)')
    if dialog.exec_():
        filename = dialog.selectedFiles()[0]
        f = open(filename, 'w')
        try:
            f.write(string)
        finally:
            f.close()
        return filename
    return None