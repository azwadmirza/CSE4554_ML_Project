def _configure_syspath():
    """Add the vendored libraries into `sys.path`."""
    # Note: These paths will be inserted into `sys.path` in reverse order (LIFO)
    # So the last path on this list will be inserted as the first path on `sys.path`
    # right after the current working dir.
    # For example: [ cwd, pathN, ..., path1, path0, <rest_of_sys.path> ]

    paths_to_insert = [
        _lib_location(),
        _ext_lib_location()
    ]

    if sys.version_info[0] == 2:
        # Add Python 2-only vendored libraries
        paths_to_insert.extend([
            # path_to_lib2,
            # path_to_ext2
        ])
    elif sys.version_info[0] == 3:
        # Add Python 3-only vendored libraries
        paths_to_insert.extend([
            # path_to_lib3,
            # path_to_ext3
        ])

    # Insert paths into `sys.path` and handle `.pth` files
    # Inspired by: https://bugs.python.org/issue7744
    for dirpath in paths_to_insert:
        # Clear `sys.path`
        sys.path, remainder = sys.path[:1], sys.path[1:]
        # Add directory as a site-packages directory and handle `.pth` files
        site.addsitedir(dirpath)
        # Restore rest of `sys.path`
        sys.path.extend(remainder)