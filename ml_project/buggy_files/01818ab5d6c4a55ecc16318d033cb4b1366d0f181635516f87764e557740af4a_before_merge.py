def read_program(path: str, pyversion: Tuple[int, int]) -> str:
    try:
        text = read_with_python_encoding(path, pyversion)
    except IOError as ioerr:
        raise CompileError([
            "mypy: can't read file '{}': {}".format(path, ioerr.strerror)])
    return text