def clear_non_release_groups(filepath):
    """Remove non release groups from the name of the given file path.

    It also renames/moves the file to the path

    :param filepath: the file path
    :type filepath: str
    :return: the new file path
    :rtype: str
    """
    try:
        # Remove non release groups from video file. Needed to match subtitles
        new_filepath = remove_non_release_groups(filepath)
        if new_filepath != filepath:
            os.rename(filepath, new_filepath)
            filepath = new_filepath
    except Exception as error:
        logger.debug(u"Couldn't remove non release groups from video file. Error: %s", ex(error))

    return filepath