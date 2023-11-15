    async def _get_java_version() -> Tuple[int, int]:
        """This assumes we've already checked that java exists."""
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

        lines = version_info.splitlines()
        for line in lines:
            match = _RE_JAVA_VERSION_LINE.search(line)
            short_match = _RE_JAVA_SHORT_VERSION.search(line)
            if match:
                return int(match["major"]), int(match["minor"])
            elif short_match:
                return int(short_match["major"]), 0

        raise RuntimeError(
            "The output of `java -version` was unexpected. Please report this issue on Red's "
            "issue tracker."
        )