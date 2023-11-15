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
    except (IOError, ArchiveError) as error:
        log.debug('Failed to open file as archive: %s (%s)', path, error)

    return False