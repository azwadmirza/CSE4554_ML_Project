def get_context_from_db_entry_ipa(db_entry):
    """Return the context for IPA from DB"""
    try:
        logger.info("Analysis is already Done. Fetching data from the DB...")
        context = {
            'title': db_entry[0].TITLE,
            'file_name': db_entry[0].FILE_NAME,
            'size': db_entry[0].SIZE,
            'md5': db_entry[0].MD5,
            'sha1': db_entry[0].SHA1,
            'sha256': db_entry[0].SHA256,
            'plist': db_entry[0].INFOPLIST,
            'bin_name': db_entry[0].BINNAME,
            'id': db_entry[0].IDF,
            'build': db_entry[0].BUILD,
            'version': db_entry[0].VERSION,
            'sdk': db_entry[0].SDK,
            'pltfm': db_entry[0].PLTFM,
            'min': db_entry[0].MINX,
            'bin_anal': python_list(db_entry[0].BIN_ANAL),
            'libs': python_list(db_entry[0].LIBS),
            'files': python_list(db_entry[0].FILES),
            'file_analysis': python_list(db_entry[0].SFILESX),
            'strings': python_list(db_entry[0].STRINGS),
            'permissions': python_list(db_entry[0].PERMISSIONS),
            'insecure_connections': python_list(db_entry[0].INSECCON),
            'bundle_name': db_entry[0].BUNDLE_NAME,
            'bundle_url_types': python_list(db_entry[0].BUNDLE_URL_TYPES),
            'bundle_supported_platforms': python_list(db_entry[0].BUNDLE_SUPPORTED_PLATFORMS),
            'bundle_localizations': python_list(db_entry[0].BUNDLE_LOCALIZATIONS),

        }
        return context
    except:
        PrintException("[ERROR] Fetching from DB")