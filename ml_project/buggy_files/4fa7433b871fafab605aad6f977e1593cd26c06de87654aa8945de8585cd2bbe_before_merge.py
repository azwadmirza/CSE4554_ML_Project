def update_db_entry_ipa(app_dict, info_dict, bin_dict, files, sfiles):
    """Update an IPA DB entry"""
    try:
        # pylint: disable=E1101
        StaticAnalyzerIPA.objects.filter(MD5=app_dict["md5_hash"]).update(
            TITLE='Static Analysis',
            FILE_NAME=app_dict["file_name"],
            SIZE=app_dict["size"],
            MD5=app_dict["md5_hash"],
            SHA1=app_dict["sha1"],
            SHA256=app_dict["sha256"],
            INFOPLIST=info_dict["plist_xml"],
            BINNAME=info_dict["bin_name"],
            IDF=info_dict["id"],
            BUILD=info_dict["build"],
            VERSION=info_dict["bundle_version_name"],
            SDK=info_dict["sdk"],
            PLTFM=info_dict["pltfm"],
            MINX=info_dict["min"],
            BIN_ANAL=bin_dict["bin_res"],
            LIBS=bin_dict["libs"],
            FILES=files,
            SFILESX=sfiles,
            STRINGS=bin_dict["strings"],
            PERMISSIONS=info_dict["permissions"],
            INSECCON=info_dict["inseccon"],
            BUNDLE_NAME=info_dict["bundle_name"],
            BUNDLE_URL_TYPES=info_dict["bundle_url_types"],
            BUNDLE_SUPPORTED_PLATFORMS=info_dict["bundle_supported_platforms"],
            BUNDLE_LOCALIZATIONS=info_dict["bundle_localizations"],
        )

    except:
        PrintException("[ERROR] Updating DB")