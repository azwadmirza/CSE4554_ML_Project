def get_manifest(app_path, app_dir, tools_dir, typ, binary):
    """Get the manifest file."""
    try:
        manifest = None
        dat = read_manifest(app_dir, app_path, tools_dir, typ, binary)
        try:
            logger.info("Parsing AndroidManifest.xml")
            manifest = minidom.parseString(dat)
        except:
            PrintException(
                "[ERROR] apktool failed to extract AndroidManifest.xml or parsing failed")
            manifest = minidom.parseString(
                (
                    r'<?xml version="1.0" encoding="utf-8"?><manifest xmlns:android='
                    r'"http://schemas.android.com/apk/res/android" android:versionCode="Failed"  '
                    r'android:versionName="Failed" package="Failed"  '
                    r'platformBuildVersionCode="Failed" '
                    r'platformBuildVersionName="Failed XML Parsing" ></manifest>'
                )
            )
            logger.warning("Using Fake XML to continue the Analysis")
        return manifest
    except:
        PrintException("[ERROR] Parsing Manifest file")