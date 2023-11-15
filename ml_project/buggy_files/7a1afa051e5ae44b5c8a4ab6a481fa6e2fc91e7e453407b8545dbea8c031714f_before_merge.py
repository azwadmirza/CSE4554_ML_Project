def find_catalog_files(docname, srcdir, locale_dirs, lang, compaction):
    # type: (unicode, unicode, List[unicode], unicode, bool) -> List[unicode]
    if not(lang and locale_dirs):
        return []

    domain = find_catalog(docname, compaction)
    files = [gettext.find(domain, path.join(srcdir, dir_), [lang])  # type: ignore
             for dir_ in locale_dirs]
    files = [path.relpath(f, srcdir) for f in files if f]  # type: ignore
    return files  # type: ignore