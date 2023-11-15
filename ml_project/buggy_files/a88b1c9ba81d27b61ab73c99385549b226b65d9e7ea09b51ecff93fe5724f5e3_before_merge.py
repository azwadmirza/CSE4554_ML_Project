def propose_interpreters(spec, app_data):
    # 1. if it's an absolute path and exists, use that
    if spec.is_abs and os.path.exists(spec.path):
        yield PythonInfo.from_exe(spec.path, app_data), True

    # 2. try with the current
    yield PythonInfo.current_system(app_data), True

    # 3. otherwise fallback to platform default logic
    if IS_WIN:
        from .windows import propose_interpreters

        for interpreter in propose_interpreters(spec, app_data):
            yield interpreter, True

    paths = get_paths()
    # find on path, the path order matters (as the candidates are less easy to control by end user)
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