    async def _get_jar_args(cls) -> List[str]:
        java_available, java_version = await cls._has_java()
        if not java_available:
            raise RuntimeError("You must install Java 1.8+ for Lavalink to run.")

        if java_version == (1, 8):
            extra_flags = ["-Dsun.zip.disableMemoryMapping=true"]
        elif java_version >= (11, 0):
            extra_flags = ["-Djdk.tls.client.protocols=TLSv1.2"]
        else:
            extra_flags = []

        return ["java", *extra_flags, "-jar", str(LAVALINK_JAR_FILE)]