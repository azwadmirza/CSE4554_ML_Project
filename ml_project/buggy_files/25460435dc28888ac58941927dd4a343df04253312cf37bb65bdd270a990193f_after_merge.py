def get_egg_info(prefix, all_pkgs=False):
    """
    Return a set of canonical names of all Python packages (in `prefix`),
    by inspecting the .egg-info files inside site-packages.
    By default, only untracked (not conda installed) .egg-info files are
    considered.  Setting `all_pkgs` to True changes this.
    """
    installed_pkgs = linked_data(prefix)
    sp_dir = get_site_packages_dir(installed_pkgs)
    if sp_dir is None:
        return set()

    conda_files = set()
    for info in itervalues(installed_pkgs):
        conda_files.update(info.get('files', []))

    res = set()
    for path in get_egg_info_files(join(prefix, sp_dir)):
        f = rel_path(prefix, path)
        if all_pkgs or f not in conda_files:
            try:
                dist = parse_egg_info(path)
            except UnicodeDecodeError:
                dist = None
            if dist:
                res.add(dist)
    return res