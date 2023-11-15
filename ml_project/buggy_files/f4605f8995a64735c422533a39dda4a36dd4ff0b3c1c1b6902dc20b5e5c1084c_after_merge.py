def _find_rcc_or_raise() -> str:
    """Locate the Qt rcc binary to generate resource files

    1. we always want to use pyrcc5 if it's available, regardless of API
    2. it will sometimes, (if not always) be named pyrcc5.bat on windows...
       but shutil.which() will find that too
    3. We also want to prefer binaries higher up on the path, and we add
       sys.executable to the front of the path (and \\Scripts on windows)
    4. after pyrcc5 we try pyside2-rcc

    see https://github.com/napari/napari/issues/1221
    and https://github.com/napari/napari/issues/1254

    Returns
    -------
    path : str
        Path to the located rcc binary, or None if not found

    Raises
    ------
    FileNotFoundError
        If no executable can be found.
    """
    python_dir = os.path.dirname(sys.executable)
    paths = [python_dir, os.environ.get("PATH", '')]
    if os.name == 'nt':
        paths.insert(0, os.path.join(python_dir, 'Scripts'))
    # inject bundle binary path if it exists
    bundle_bin = bundle_bin_dir()
    if bundle_bin:
        paths.insert(0, bundle_bin)
    path = os.pathsep.join(paths)

    for bin_name in ('pyrcc5', 'pyside2-rcc'):
        rcc_binary = shutil.which(bin_name, path=path)
        if rcc_binary:
            yield rcc_binary
    raise FileNotFoundError(
        "Unable to find an executable to build Qt resources (icons).\n"
        "Tried: 'pyrcc5.bat', 'pyrcc5', 'pyside2-rcc'.\n"
        "Please open issue at https://github.com/napari/napari/issues/."
    )