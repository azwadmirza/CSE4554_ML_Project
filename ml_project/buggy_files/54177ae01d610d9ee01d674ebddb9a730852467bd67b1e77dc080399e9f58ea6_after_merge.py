def plist_analysis(src, is_source):
    """Plist Analysis"""
    try:
        logger.info("iOS Info.plist Analysis Started")
        plist_info = {
            "bin_name": "",
            "bin": "",
            "id": "",
            "version": "",
            "build": "",
            "sdk": "",
            "pltfm": "",
            "min": "",
            "plist_xml": "",
            "permissions": [],
            "inseccon": [],
            "bundle_name": "",
            "build_version_name": "",
            "bundle_url_types": [],
            "bundle_supported_platforms": [],
            "bundle_localizations": []
        }
        plist_file = None
        if is_source:
            logger.info("Finding Info.plist in iOS Source")
            for ifile in os.listdir(src):
                if ifile.endswith(".xcodeproj"):
                    app_name = ifile.replace(".xcodeproj", "")
                    break
            app_plist_file = "Info.plist"
            for dirpath, dirnames, files in os.walk(src):
                for name in files:
                    if "__MACOSX" not in dirpath and name == app_plist_file:
                        plist_file = os.path.join(dirpath, name)
                        break
        else:
            logger.info("Finding Info.plist in iOS Binary")
            dirs = os.listdir(src)
            dot_app_dir = ""
            for dir_ in dirs:
                if dir_.endswith(".app"):
                    dot_app_dir = dir_
                    break
            bin_dir = os.path.join(src, dot_app_dir) # Full Dir/Payload/x.app
            plist_file = os.path.join(bin_dir, "Info.plist")
        if not isFileExists(plist_file):
            logger.warning("Cannot find Info.plist file. Skipping Plist Analysis.")
        else:
            #Generic Plist Analysis
            plist_obj = plistlib.readPlist(plist_file)
            plist_info["plist_xml"] = plistlib.writePlistToBytes(plist_obj).decode("utf-8", "ignore")
            if "CFBundleDisplayName" in plist_obj:
                plist_info["bin_name"] = plist_obj["CFBundleDisplayName"]
            else:
                if not is_source:
                    #For iOS IPA
                    plist_info["bin_name"] = dot_app_dir.replace(".app", "")
            if "CFBundleExecutable" in plist_obj:
                plist_info["bin"] = plist_obj["CFBundleExecutable"]
            if "CFBundleIdentifier" in plist_obj:
                plist_info["id"] = plist_obj["CFBundleIdentifier"]

            # build
            if "CFBundleVersion" in plist_obj:
                plist_info["build"] = plist_obj["CFBundleVersion"]
            if "DTSDKName" in plist_obj:
                plist_info["sdk"] = plist_obj["DTSDKName"]
            if "DTPlatformVersion" in plist_obj:
                plist_info["pltfm"] = plist_obj["DTPlatformVersion"]
            if "MinimumOSVersion" in plist_obj:
                plist_info["min"] = plist_obj["MinimumOSVersion"]

            plist_info["bundle_name"] = plist_obj.get("CFBundleName", "")
            plist_info["bundle_version_name"] = plist_obj.get("CFBundleShortVersionString", "")
            plist_info["bundle_url_types"] = plist_obj.get("CFBundleURLTypes", [])
            plist_info["bundle_supported_platforms"] = plist_obj.get("CFBundleSupportedPlatforms", [])
            plist_info["bundle_localizations"] = plist_obj.get("CFBundleLocalizations", [])

            # Check possible app-permissions
            plist_info["permissions"] = __check_permissions(plist_obj)
            plist_info["inseccon"] = __check_insecure_connections(plist_obj)
        return plist_info
    except:
        PrintException("Reading from Info.plist")