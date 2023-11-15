    def from_line(cls, line):
        link = None
        path = None
        editable = line.startswith("-e ")
        line = line.split(" ", 1)[1] if editable else line
        if not any([is_installable_file(line), is_valid_url(line)]):
            raise ValueError(
                "Supplied requirement is not installable: {0!r}".format(line)
            )

        if is_valid_url(line):
            link = Link(line)
        else:
            _path = Path(line)
            link = Link(_path.absolute().as_uri())
            if _path.is_absolute() or _path.as_posix() == ".":
                path = _path.as_posix()
            else:
                path = get_converted_relative_path(line)
        arg_dict = {
            "path": path,
            "uri": link.url_without_fragment,
            "link": link,
            "editable": editable,
        }
        if link.egg_fragment:
            arg_dict["name"] = link.egg_fragment
        created = cls(**arg_dict)
        return created