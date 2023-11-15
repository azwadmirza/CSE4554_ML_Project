def init(locale_dirs, language, catalog='sphinx'):
    """Look for message catalogs in `locale_dirs` and *ensure* that there is at
    least a NullTranslations catalog set in `translators`.  If called multiple
    times or if several ``.mo`` files are found, their contents are merged
    together (thus making ``init`` reentrable).
    """
    global translators
    translator = translators.get(catalog)
    # ignore previously failed attempts to find message catalogs
    if isinstance(translator, gettext.NullTranslations):
        translator = None
    # the None entry is the system's default locale path
    has_translation = True

    # compile mo files if po file is updated
    # TODO: remove circular importing
    from sphinx.util.i18n import find_catalog_source_files
    for catinfo in find_catalog_source_files(locale_dirs, language, domains=[catalog]):
        catinfo.write_mo(language)

    # loading
    for dir_ in locale_dirs:
        try:
            trans = gettext.translation(catalog, localedir=dir_,
                                        languages=[language])
            if translator is None:
                translator = trans
            else:
                translator._catalog.update(trans._catalog)
        except Exception:
            # Language couldn't be found in the specified path
            pass
    # guarantee translators[catalog] exists
    if translator is None:
        translator = gettext.NullTranslations()
        has_translation = False
    translators[catalog] = translator
    if hasattr(translator, 'ugettext'):
        translator.gettext = translator.ugettext
    return translator, has_translation