def unpack_rar_files(dirpath):
    """Unpacks any existing rar files present in the specified dirpath

    :param dirpath: the directory path to be used
    :type dirpath: str
    """
    for root, _, files in os.walk(dirpath, topdown=False):
        rar_files = [rar_file for rar_file in files if isRarFile(rar_file)]
        if rar_files and sickbeard.UNPACK:
            video_files = [video_file for video_file in files if isMediaFile(video_file)]
            if u'_UNPACK' not in root and (not video_files or root == sickbeard.TV_DOWNLOAD_DIR):
                logger.debug(u'Found rar files in post-process folder: %s', rar_files)
                result = processTV.ProcessResult()
                processTV.unRAR(root, rar_files, False, result)
        elif rar_files and not sickbeard.UNPACK:
            logger.warning(u'Unpack is disabled. Skipping: %s', rar_files)