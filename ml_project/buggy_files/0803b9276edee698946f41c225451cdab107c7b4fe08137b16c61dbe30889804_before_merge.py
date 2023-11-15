def delete_unwanted_subtitles(dirpath, filename):
    """Deletes unwanted subtitles for the given filename in the specified dirpath

    :param dirpath: the directory path to be used
    :type dirpath: str
    :param filename: the subtitle filename
    :type dirpath: str
    """
    if not sickbeard.SUBTITLES_MULTI or not sickbeard.SUBTITLES_KEEP_ONLY_WANTED or \
            filename.rpartition('.')[2] not in subtitle_extensions:
        return

    code = filename.rsplit('.', 2)[1].lower().replace('_', '-')
    language = from_code(code, unknown='') or from_ietf_code(code, unknown='und')

    if language.opensubtitles not in sickbeard.SUBTITLES_LANGUAGES:
        try:
            os.remove(os.path.join(dirpath, filename))
            logger.debug(u"Deleted '%s' because we don't want subtitle language '%s'. We only want '%s' language(s)",
                         filename, language, ','.join(sickbeard.SUBTITLES_LANGUAGES))
        except Exception as error:
            logger.info(u"Couldn't delete subtitle: %s. Error: %s", filename, ex(error))