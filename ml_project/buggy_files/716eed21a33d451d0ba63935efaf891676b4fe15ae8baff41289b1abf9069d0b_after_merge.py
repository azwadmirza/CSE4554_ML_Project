def parse_m3u(filelike, pl_name, library=None):
    filenames = []
    for line in filelike:
        line = line.strip()
        if line.startswith(b"#"):
            continue
        __attempt_add(line, filenames)
    return __create_playlist(pl_name, _dir_for(filelike), filenames, library)