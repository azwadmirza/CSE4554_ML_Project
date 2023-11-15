def MusicFile(filename):
    """Returns a AudioFile instance or None"""

    loader = get_loader(filename)
    if loader is not None:
        try:
            return loader(filename)
        except AudioFileError:
            print_w("Error loading %r" % filename)
            util.print_exc()