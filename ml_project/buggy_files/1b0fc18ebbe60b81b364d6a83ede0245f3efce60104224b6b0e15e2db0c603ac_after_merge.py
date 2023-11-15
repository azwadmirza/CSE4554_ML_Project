def get_default_version() -> str:
    if all(helpers.exe_exists(exe) for exe in ('ruby', 'gem')):
        return 'system'
    else:
        return C.DEFAULT