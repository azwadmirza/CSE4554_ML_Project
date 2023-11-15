def hardlink_file(src_file, dest_file):
    """Create a hard-link (inside filesystem link) between source and destination.

    :param src_file: Source file
    :type src_file: str
    :param dest_file: Destination file
    :type dest_file: str
    """
    try:
        link(src_file, dest_file)
        fix_set_group_id(dest_file)
    except OSError as msg:
        if hasattr(msg, 'errno') and msg.errno == 17:
            # File exists. Don't fallback to copy
            log.warning(
                u'Failed to create hardlink of {source} at {destination}.'
                u' Error: {error!r}', {
                    'source': src_file,
                    'destination': dest_file,
                    'error': msg
                }
            )
        else:
            log.warning(
                u'Failed to create hardlink of {source} at {destination}.'
                u' Error: {error!r}. Copying instead', {
                    'source': src_file,
                    'destination': dest_file,
                    'error': msg,
                }
            )
            copy_file(src_file, dest_file)