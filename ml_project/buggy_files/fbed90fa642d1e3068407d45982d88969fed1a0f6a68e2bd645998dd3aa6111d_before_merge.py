def get_workspace(path, format):
    import viv_utils

    logger.debug("generating vivisect workspace for: %s", path)
    if format == "auto":
        if not is_supported_file_type(path):
            raise UnsupportedFormatError()
        vw = viv_utils.getWorkspace(path)
    elif format == "pe":
        vw = viv_utils.getWorkspace(path)
    elif format == "sc32":
        vw = get_shellcode_vw(path, arch="i386")
    elif format == "sc64":
        vw = get_shellcode_vw(path, arch="amd64")
    logger.debug("%s", get_meta_str(vw))
    return vw