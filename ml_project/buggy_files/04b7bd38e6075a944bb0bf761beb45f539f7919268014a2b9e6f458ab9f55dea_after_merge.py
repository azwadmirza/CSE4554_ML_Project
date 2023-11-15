    async def _is_up_to_date(cls):
        if cls._up_to_date is True:
            # Return cached value if we've checked this before
            return True
        args = await cls._get_jar_args()
        args.append("--version")
        _proc = await asyncio.subprocess.create_subprocess_exec(  # pylint:disable=no-member
            *args,
            cwd=str(LAVALINK_DOWNLOAD_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout = (await _proc.communicate())[0]
        match = _RE_BUILD_LINE.search(stdout)
        if not match:
            # Output is unexpected, suspect corrupted jarfile
            return False
        build = int(match["build"])
        cls._up_to_date = build >= JAR_BUILD
        return cls._up_to_date