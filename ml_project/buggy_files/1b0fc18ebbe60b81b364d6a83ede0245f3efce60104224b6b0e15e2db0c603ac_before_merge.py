def get_default_version() -> str:
    if all(parse_shebang.find_executable(exe) for exe in ('ruby', 'gem')):
        return 'system'
    else:
        return C.DEFAULT