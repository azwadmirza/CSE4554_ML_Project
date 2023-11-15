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
        import subprocess
        subprocess.Popen(['xmessage', '-center', text], shell=False)
    sep = "*" * 20
    print('\n'.join([sep, title, sep, text, sep]), file=sys.stderr)