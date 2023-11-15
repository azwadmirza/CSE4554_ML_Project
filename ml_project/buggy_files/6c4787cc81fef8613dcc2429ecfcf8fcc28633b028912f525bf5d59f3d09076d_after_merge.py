def parse_pls(filelike, pl_name, library=None):
    filenames = []
    for line in filelike:
        line = line.strip()
        if not line.lower().startswith(b"file"):
            continue
        fn = line[line.index(b"=") + 1:].strip()
        __attempt_add(fn, filenames)
    return __create_playlist(pl_name, _dir_for(filelike), filenames, library)