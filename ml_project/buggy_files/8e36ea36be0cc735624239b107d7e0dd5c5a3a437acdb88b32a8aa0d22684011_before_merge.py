def _is_hidden_win(path):
    """Return whether or not a file is hidden on Windows.

    This uses GetFileAttributes to work out if a file has the "hidden" flag
    (FILE_ATTRIBUTE_HIDDEN).
    """
    # FILE_ATTRIBUTE_HIDDEN = 2 (0x2) from GetFileAttributes documentation.
    hidden_mask = 2

    # Retrieve the attributes for the file.
    attrs = ctypes.windll.kernel32.GetFileAttributesW(path)

    # Ensure we have valid attribues and compare them against the mask.
    return attrs >= 0 and attrs & hidden_mask