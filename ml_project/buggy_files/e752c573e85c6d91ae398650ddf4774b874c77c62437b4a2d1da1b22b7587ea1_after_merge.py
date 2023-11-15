async def has_java(loop) -> Tuple[bool, Optional[_JavaVersion]]:
    java_available = shutil.which("java") is not None
    if not java_available:
        return False, None

    version = await get_java_version(loop)
    return (2, 0) > version >= (1, 8) or version >= (8, 0), version