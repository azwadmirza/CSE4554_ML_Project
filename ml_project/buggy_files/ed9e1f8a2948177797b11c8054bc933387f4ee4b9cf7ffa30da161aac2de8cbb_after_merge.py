def cleanup_for_venv(venv):
    within_parallel = PARALLEL_ENV_VAR_KEY_PRIVATE in os.environ
    # if the directory exists and it doesn't look like a virtualenv, produce
    # an error
    if venv.path.exists():
        dir_items = set(os.listdir(str(venv.path))) - {".lock", "log"}
        dir_items = {p for p in dir_items if not p.startswith(".tox-") or p == ".tox-config1"}
    else:
        dir_items = set()

    if not (
        # doesn't exist => OK
        not venv.path.exists()
        # does exist, but it's empty => OK
        or not dir_items
        # tox has marked this as an environment it has created in the past
        or ".tox-config1" in dir_items
        # it exists and we're on windows with Lib and Scripts => OK
        or (INFO.IS_WIN and dir_items > {"Scripts", "Lib"})
        # non-windows, with lib and bin => OK
        or dir_items > {"bin", "lib"}
        # pypy has a different lib folder => OK
        or dir_items > {"bin", "lib_pypy"}
    ):
        venv.status = "error"
        reporter.error(
            "cowardly refusing to delete `envdir` (it does not look like a virtualenv): "
            "{}".format(venv.path)
        )
        raise SystemExit(2)

    if within_parallel:
        if venv.path.exists():
            # do not delete the log folder as that's used by parent
            for content in venv.path.listdir():
                if not content.basename == "log":
                    content.remove(rec=1, ignore_errors=True)
    else:
        ensure_empty_dir(venv.path)