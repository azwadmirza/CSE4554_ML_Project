def get_icon(apk_path, res_dir):
    """Returns a dict with isHidden boolean and a relative path
        path is a full path (not relative to resource folder) """
    try:
        logger.info("Fetching icon path")
        a = apk.APK(apk_path)
        icon_resolution = 0xFFFE - 1
        icon_name = a.get_app_icon(max_dpi=icon_resolution)
        if icon_name:
            return {
                'path': os.path.join(os.path.dirname(apk_path), icon_name),
                'hidden': False
            }
        return {
            'path': guess_icon_path(res_dir),
            'hidden': True
        }
    except:
        PrintException("Fetching icon function")