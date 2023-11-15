def _af_for(filename, library, pl_dir):
    full_path = os.path.join(pl_dir, filename)
    filename = os.path.realpath(full_path)

    af = None
    if library:
        af = library.get_filename(filename)
    if af is None:
        af = formats.MusicFile(filename)
    return af