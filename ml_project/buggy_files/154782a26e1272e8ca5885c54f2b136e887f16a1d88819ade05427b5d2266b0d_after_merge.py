def get_firefox_binary_path():
    """
    If ../../firefox-bin/firefox-bin or os.environ["FIREFOX_BINARY"] exists,
    return it. Else, throw a RuntimeError.
    """
    if "FIREFOX_BINARY" in os.environ:
        firefox_binary_path = os.environ["FIREFOX_BINARY"]
        if not os.path.isfile(firefox_binary_path):
            raise RuntimeError(
                "No file found at the path specified in "
                "environment variable `FIREFOX_BINARY`."
                "Current `FIREFOX_BINARY`: %s" % firefox_binary_path)
        return firefox_binary_path

    root_dir = os.path.dirname(__file__) + "/../.."
    if platform == 'darwin':
        firefox_binary_path = os.path.abspath(root_dir +
                                              "/Nightly.app/Contents/MacOS/firefox-bin")
    else:
        firefox_binary_path = os.path.abspath(root_dir +
                                              "/firefox-bin/firefox-bin")

    if not os.path.isfile(firefox_binary_path):
        raise RuntimeError(
            "The `firefox-bin/firefox-bin` binary is not found in the root "
            "of the  OpenWPM directory (did you run the install script "
            "(`install.sh`)?). Alternatively, you can specify a binary "
            "location using the OS environment variable FIREFOX_BINARY.")
    return firefox_binary_path