def _af_for(filename, library, pl_filename):
    full_path = os.path.join(os.path.dirname(pl_filename), filename)
    filename = os.path.realpath(full_path)
    if library:
        try:
            return library[filename]
        except KeyError:
            pass
    return formats.MusicFile(filename)