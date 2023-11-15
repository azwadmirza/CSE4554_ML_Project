async def get_java_version(loop) -> _JavaVersion:
    """
    This assumes we've already checked that java exists.
    """
    proc = Popen(shlex.split("java -version", posix=os.name == "posix"), stdout=PIPE, stderr=PIPE)
    _, err = proc.communicate()

    version_info = str(err, encoding="utf-8")

    version_line = version_info.split("\n")[0]
    version_start = version_line.find('"')
    version_string = version_line[version_start + 1 : -1]
    major, minor = version_string.split(".")[:2]
    return int(major), int(minor)