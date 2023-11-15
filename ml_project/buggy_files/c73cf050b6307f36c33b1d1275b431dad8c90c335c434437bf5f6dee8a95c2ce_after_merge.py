def delete_unwanted_subtitles(dirpath, filename):
    """Delete unwanted subtitles for the given filename in the specified dirpath.

    :param dirpath: the directory path to be used
    :type dirpath: str
    :param filename: the subtitle filename
    :type dirpath: str
    """
    if not app.SUBTITLES_MULTI or not app.SUBTITLES_KEEP_ONLY_WANTED or \
            filename.rpartition('.')[2] not in subtitle_extensions:
        return

    code = filename.rsplit('.', 2)[1].lower().replace('_', '-')
    language = from_code(code, unknown='') or from_ietf_code(code)
    found_language = None
    try:
        found_language = language.opensubtitles
    except LanguageConvertError:
        logger.info(u"Unable to convert language code '%s' for: %s", code, filename)

    if found_language and found_language not in app.SUBTITLES_LANGUAGES:
        try:
            os.remove(os.path.join(dirpath, filename))
        except OSError as error:
            logger.info(u"Couldn't delete subtitle: %s. Error: %s", filename, ex(error))
        else:
            logger.debug(u"Deleted '%s' because we don't want subtitle language '%s'. We only want '%s' language(s)",
                         filename, language, ','.join(app.SUBTITLES_LANGUAGES))