def find_catalog_source_files(locale_dirs, locale, domains=None, gettext_compact=None,
                              charset='utf-8', force_all=False,
                              excluded=Matcher([])):
    # type: (List[unicode], unicode, List[unicode], bool, unicode, bool, Matcher) -> Set[CatalogInfo]  # NOQA
    """
    :param list locale_dirs:
       list of path as `['locale_dir1', 'locale_dir2', ...]` to find
       translation catalogs. Each path contains a structure such as
       `<locale>/LC_MESSAGES/domain.po`.
    :param str locale: a language as `'en'`
    :param list domains: list of domain names to get. If empty list or None
       is specified, get all domain names. default is None.
    :param boolean force_all:
       Set True if you want to get all catalogs rather than updated catalogs.
       default is False.
    :return: [CatalogInfo(), ...]
    """
    if gettext_compact is not None:
        warnings.warn('gettext_compact argument for find_catalog_source_files() '
                      'is deprecated.', RemovedInSphinx30Warning)

    catalogs = set()  # type: Set[CatalogInfo]

    if not locale:
        return catalogs  # locale is not specified

    for locale_dir in locale_dirs:
        if not locale_dir:
            continue  # skip system locale directory

        base_dir = path.join(locale_dir, locale, 'LC_MESSAGES')

        if not path.exists(base_dir):
            continue  # locale path is not found

        for dirpath, dirnames, filenames in walk(base_dir, followlinks=True):
            filenames = [f for f in filenames if f.endswith('.po')]
            for filename in filenames:
                if excluded(path.join(relpath(dirpath, base_dir), filename)):
                    continue
                base = path.splitext(filename)[0]
                domain = relpath(path.join(dirpath, base), base_dir).replace(path.sep, SEP)
                if domains and domain not in domains:
                    continue
                cat = CatalogInfo(base_dir, domain, charset)
                if force_all or cat.is_outdated():
                    catalogs.add(cat)

    return catalogs