    async def _get_java_version() -> Tuple[int, int]:
        """
        This assumes we've already checked that java exists.
        """
        _proc: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(  # pylint:disable=no-member
            "java", "-version", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
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
        version_line_re = re.compile(
            r'version "(?P<major>\d+).(?P<minor>\d+).\d+(?:_\d+)?(?:-[A-Za-z0-9]+)?"'
        )
        short_version_re = re.compile(r'version "(?P<major>\d+)"')

        lines = version_info.splitlines()
        for line in lines:
            match = version_line_re.search(line)
            short_match = short_version_re.search(line)
            if match:
                return int(match["major"]), int(match["minor"])
            elif short_match:
                return int(short_match["major"]), 0

        raise RuntimeError(
            "The output of `java -version` was unexpected. Please report this issue on Red's "
            "issue tracker."
        )