def gen_downloads(app_dir, md5, icon_path=''):
    """Generate downloads for java and smali."""
    try:
        logger.info("Generating Downloads")
        # For Java
        directory = os.path.join(app_dir, 'java_source/')
        dwd_dir = os.path.join(settings.DWD_DIR, md5 + '-java.zip')
        zipf = zipfile.ZipFile(dwd_dir, 'w')
        zipdir(directory, zipf)
        zipf.close()
        # For Smali
        directory = os.path.join(app_dir, 'smali_source/')
        dwd_dir = os.path.join(settings.DWD_DIR, md5 + '-smali.zip')
        zipf = zipfile.ZipFile(dwd_dir, 'w')
        zipdir(directory, zipf)
        zipf.close()
        # Icon
        icon_path = icon_path.encode('utf-8')
        if icon_path:
            if os.path.exists(icon_path):
                shutil.copy2(icon_path, os.path.join(
                    settings.DWD_DIR, md5 + '-icon.png'))

    except:
        PrintException("Generating Downloads")