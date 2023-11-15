async def has_java(loop) -> Tuple[bool, Optional[_JavaVersion]]:
    java_available = shutil.which("java") is not None
    if not java_available:
        return False, None

    version = await get_java_version(loop)
    return version >= (1, 8), version