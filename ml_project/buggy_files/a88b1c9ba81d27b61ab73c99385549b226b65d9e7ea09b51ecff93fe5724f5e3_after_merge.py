def propose_interpreters(spec, app_data):
    # 1. if it's a path and exists
    if spec.path is not None:
        try:
            os.lstat(spec.path)  # Windows Store Python does not work with os.path.exists, but does for os.lstat
        except OSError:
            if spec.is_abs:
                raise
        else:
            yield PythonInfo.from_exe(os.path.abspath(spec.path), app_data), True
        if spec.is_abs:
            return
    else:
        # 2. otherwise try with the current
        yield PythonInfo.current_system(app_data), True

        # 3. otherwise fallback to platform default logic
        if IS_WIN:
            from .windows import propose_interpreters

            for interpreter in propose_interpreters(spec, app_data):
                yield interpreter, True
    # finally just find on path, the path order matters (as the candidates are less easy to control by end user)
    paths = get_paths()
    tested_exes = set()
    for pos, path in enumerate(paths):
        path = ensure_text(path)
        logging.debug(LazyPathDump(pos, path))
        for candidate, match in possible_specs(spec):
            found = check_path(candidate, path)
            if found is not None:
                exe = os.path.abspath(found)
                if exe not in tested_exes:
                    tested_exes.add(exe)
                    interpreter = PathPythonInfo.from_exe(exe, app_data, raise_on_error=False)
                    if interpreter is not None:
                        yield interpreter, match