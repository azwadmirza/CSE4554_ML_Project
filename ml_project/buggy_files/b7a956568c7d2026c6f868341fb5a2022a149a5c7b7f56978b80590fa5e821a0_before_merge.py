def find_catalog_source_files(locale_dirs, locale, domains=None, gettext_compact=False,
                              charset='utf-8', force_all=False):
    # type: (List[unicode], unicode, List[unicode], bool, unicode, bool) -> Set[CatalogInfo]
    """
    :param list locale_dirs:
       list of path as `['locale_dir1', 'locale_dir2', ...]` to find
       translation catalogs. Each path contains a structure such as
       `<locale>/LC_MESSAGES/domain.po`.
    :param str locale: a language as `'en'`
    :param list domains: list of domain names to get. If empty list or None
       is specified, get all domain names. default is None.
    :param boolean gettext_compact:
       * False: keep domains directory structure (default).
       * True: domains in the sub directory will be merged into 1 file.
    :param boolean force_all:
       Set True if you want to get all catalogs rather than updated catalogs.
       default is False.
    :return: [CatalogInfo(), ...]
    """
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
                base = path.splitext(filename)[0]
                domain = path.relpath(path.join(dirpath, base), base_dir)
                if gettext_compact and path.sep in domain:
                    domain = path.split(domain)[0]
                domain = domain.replace(path.sep, SEP)
                if domains and domain not in domains:
                    continue
                cat = CatalogInfo(base_dir, domain, charset)
                if force_all or cat.is_outdated():
                    catalogs.add(cat)

    return catalogs