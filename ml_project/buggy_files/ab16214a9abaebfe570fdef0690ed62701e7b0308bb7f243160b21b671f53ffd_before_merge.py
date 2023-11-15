def tkinter_clipboard_get():
    """ Get the clipboard's text using Tkinter.

    This is the default on systems that are not Windows or OS X. It may
    interfere with other UI toolkits and should be replaced with an
    implementation that uses that toolkit.
    """
    try:
        import Tkinter
    except ImportError:
        raise TryNext("Getting text from the clipboard on this platform "
                      "requires Tkinter.")
    root = Tkinter.Tk()
    root.withdraw()
    text = root.clipboard_get()
    root.destroy()
    return text