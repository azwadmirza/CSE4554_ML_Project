def get_default_version() -> str:
    # nodeenv does not yet support `-n system` on windows
    if sys.platform == 'win32':
        return C.DEFAULT
    # if node is already installed, we can save a bunch of setup time by
    # using the installed version
    elif all(parse_shebang.find_executable(exe) for exe in ('node', 'npm')):
        return 'system'
    else:
        return C.DEFAULT