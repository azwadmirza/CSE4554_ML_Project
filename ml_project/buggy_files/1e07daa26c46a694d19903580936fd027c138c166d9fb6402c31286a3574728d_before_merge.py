def _do_popup(title, text):
    """
    Create a native pop-up without any third party dependency.

    :param title: the pop-up title
    :param text: the pop-up body
    """
    try:
        import win32api
        win32api.MessageBox(0, text, title)
    except ImportError:
        os.system('xmessage -center "$(printf "%s")"' % (text))
    sep = "*" * 20
    print('\n'.join([sep, title, sep, text, sep]), file=sys.stderr)