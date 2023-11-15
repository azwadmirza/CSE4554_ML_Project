def update_db_entry_ios(app_dict, info_dict, code_dict, files, sfiles):
    """Update an IOS ZIP DB entry"""
    try:
        # pylint: disable=E1101
        StaticAnalyzerIOSZIP.objects.filter(MD5=app_dict["md5_hash"]).update(
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
            FILES=files,
            SFILESX=sfiles,
            API=code_dict["api"],
            CODEANAL=code_dict["code_anal"],
            URLnFile=code_dict["urlnfile"],
            DOMAINS=code_dict["domains"],
            EmailnFile=code_dict["emailnfile"],
            PERMISSIONS=info_dict["permissions"],
            INSECCON=info_dict["inseccon"],
            BUNDLE_NAME=info_dict["bundle_name"],
            BUNDLE_URL_TYPES=info_dict["bundle_url_types"],
            BUNDLE_SUPPORTED_PLATFORMS=info_dict["bundle_supported_platforms"],
            BUNDLE_LOCALIZATIONS=info_dict["bundle_localizations"]
        )

    except:
        PrintException("Updating DB")