def ParsePLS(file):
    data = {}

    lines = file.readlines()
    if not lines or "[playlist]" not in lines.pop(0):
        return []

    for line in lines:
        try:
            head, val = line.strip().split("=", 1)
        except (TypeError, ValueError):
            continue
        else:
            head = head.lower()
            if head.startswith("length") and val == "-1":
                continue
            else:
                data[head] = val.decode('utf-8', 'replace')

    count = 1
    files = []
    warnings = []
    while True:
        if "file%d" % count in data:
            filename = data["file%d" % count].encode('utf-8', 'replace')
            if filename.lower()[-4:] in [".pls", ".m3u"]:
                warnings.append(filename)
            else:
                irf = IRFile(filename)
                for key in ["title", "genre", "artist"]:
                    try:
                        irf[key] = data["%s%d" % (key, count)]
                    except KeyError:
                        pass
                try:
                    irf["~#length"] = int(data["length%d" % count])
                except (KeyError, TypeError, ValueError):
                    pass
                files.append(irf)
        else:
            break
        count += 1

    if warnings:
        qltk.WarningMessage(
            None, _("Unsupported file type"),
            _("Station lists can only contain locations of stations, "
              "not other station lists or playlists. The following locations "
              "cannot be loaded:\n%s") %
            "\n  ".join(map(util.escape, warnings))
        ).run()

    return files