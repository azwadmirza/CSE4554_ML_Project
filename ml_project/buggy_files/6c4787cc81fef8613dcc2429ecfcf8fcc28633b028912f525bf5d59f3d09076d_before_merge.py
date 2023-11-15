def parse_pls(filename, library=None):
    pl_name = _name_for(filename)

    filenames = []
    with open(filename, "rb") as h:
        for line in h:
            line = line.strip()
            if not line.lower().startswith(b"file"):
                continue
            else:
                try:
                    line = line[line.index(b"=") + 1:].strip()
                except ValueError:
                    pass
                else:
                    try:
                        filenames.append(bytes2fsn(line, "utf-8"))
                    except ValueError:
                        continue
    return __create_playlist(pl_name, filename, filenames, library)