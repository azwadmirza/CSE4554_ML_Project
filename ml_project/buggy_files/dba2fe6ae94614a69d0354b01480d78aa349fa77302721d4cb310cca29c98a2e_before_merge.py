def compact(paths):
    """Compact a path set to contain the minimal number of paths
    necessary to contain all paths in the set. If /a/path/ and
    /a/path/to/a/file.txt are both in the set, leave only the
    shorter path."""

    sep = os.path.sep
    short_paths = set()
    for path in sorted(paths, key=len):
        should_add = any(
            path.startswith(shortpath.rstrip("*")) and
            path[len(shortpath.rstrip("*").rstrip(sep))] == sep
            for shortpath in short_paths
        )
        if not should_add:
            short_paths.add(path)
    return short_paths