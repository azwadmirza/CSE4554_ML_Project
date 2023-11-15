async def get_java_version(loop) -> _JavaVersion:
    """
    This assumes we've already checked that java exists.
    """
    _proc: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
        "java",
        "-version",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        loop=loop,
    )
    # java -version outputs to stderr
    _, err = await _proc.communicate()

    version_info: str = err.decode("utf-8")
    # We expect the output to look something like:
    #     $ java -version
    #     ...
    #     ... version "MAJOR.MINOR.PATCH[_BUILD]" ...
    #     ...
    # We only care about the major and minor parts though.
    version_line_re = re.compile(r'version "(?P<major>\d+).(?P<minor>\d+).\d+(?:_\d+)?"')

    lines = version_info.splitlines()
    for line in lines:
        match = version_line_re.search(line)
        if match:
            return int(match["major"]), int(match["minor"])

    raise RuntimeError(
        "The output of `java -version` was unexpected. Please report this issue on Red's "
        "issue tracker."
    )