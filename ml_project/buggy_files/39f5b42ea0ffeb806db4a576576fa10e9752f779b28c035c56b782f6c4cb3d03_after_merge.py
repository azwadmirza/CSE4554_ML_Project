def get_entrypoints(filename):
    # type: (str) -> Tuple[Dict[str, str], Dict[str, str]]
    if not os.path.exists(filename):
        return {}, {}

    # This is done because you can pass a string to entry_points wrappers which
    # means that they may or may not be valid INI files. The attempt here is to
    # strip leading and trailing whitespace in order to make them valid INI
    # files.
    with io.open(filename, encoding="utf-8") as fp:
        data = io.StringIO()
        for line in fp:
            data.write(line.strip())
            data.write(u"\n")
        data.seek(0)

    # get the entry points and then the script names
    entry_points = pkg_resources.EntryPoint.parse_map(data)
    console = entry_points.get('console_scripts', {})
    gui = entry_points.get('gui_scripts', {})

    def _split_ep(s):
        # type: (pkg_resources.EntryPoint) -> Tuple[str, str]
        """get the string representation of EntryPoint,
        remove space and split on '='
        """
        split_parts = str(s).replace(" ", "").split("=")
        return split_parts[0], split_parts[1]

    # convert the EntryPoint objects into strings with module:function
    console = dict(_split_ep(v) for v in console.values())
    gui = dict(_split_ep(v) for v in gui.values())
    return console, gui