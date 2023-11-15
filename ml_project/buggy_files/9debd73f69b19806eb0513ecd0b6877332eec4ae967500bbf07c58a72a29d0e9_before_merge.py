def find_new_location(dist):
    """
    Determines the download location for the given package, and the name
    of a package, if any, that must be removed to make room. If the
    given package is already in the cache, it returns its current location,
    under the assumption that it will be overwritten. If the conflict
    value is None, that means there is no other package with that same
    name present in the cache (e.g., no collision).
    """
    rec = package_cache().get(dist)
    if rec:
        return dirname((rec['files'] or rec['dirs'])[0]), None
    fname = _dist2filename(dist)
    dname = fname[:-8]
    # Look for a location with no conflicts
    # On the second pass, just pick the first location
    for p in range(2):
        for pkg_dir in pkgs_dirs:
            pkg_path = join(pkg_dir, fname)
            prefix = fname_table_.get(pkg_path)
            if p or prefix is None:
                return pkg_dir, prefix + dname if p else None