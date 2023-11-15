def is_archive(path):
    """
    Attempts to open an entry as an archive; returns True on success, False on failure.
    """

    archive = None

    try:
        archive = open_archive(path)
        if archive:
            archive.close()
            return True
    except ArchiveError as error:
        error_message = 'Failed to open file as archive: %s (%s)' % (path, error)
        log.debug(error_message)

    return False