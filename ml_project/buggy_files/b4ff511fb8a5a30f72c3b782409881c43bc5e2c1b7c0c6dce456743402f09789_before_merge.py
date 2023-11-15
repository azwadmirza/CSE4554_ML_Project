async def maybe_download_lavalink(loop, cog):
    jar_exists = LAVALINK_JAR_FILE.exists()
    current_build = redbot.core.VersionInfo(*await cog.config.current_build())

    session = ClientSession(loop=loop)

    if not jar_exists or current_build < redbot.core.version_info:
        LAVALINK_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        await download_lavalink(session)
        await cog.config.current_build.set(redbot.core.version_info.to_json())

    session.close()

    shutil.copyfile(str(BUNDLED_APP_YML_FILE), str(APP_YML_FILE))