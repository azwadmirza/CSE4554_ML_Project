def valid_android_zip(app_dir):
    """Test if this is an valid android zip."""
    try:
        logger.info("Checking for ZIP Validity and Mode")
        # Eclipse
        man = os.path.isfile(os.path.join(app_dir, "AndroidManifest.xml"))
        src = os.path.exists(os.path.join(app_dir, "src/"))
        if man and src:
            return 'eclipse', True
        # Studio
        man = os.path.isfile(
            os.path.join(
                app_dir, "app/src/main/AndroidManifest.xml"
            )
        )
        src = os.path.exists(os.path.join(app_dir, "app/src/main/java/"))
        if man and src:
            return 'studio', True
        # iOS Source
        xcode = [f for f in os.listdir(app_dir) if f.endswith(".xcodeproj")]
        if xcode:
            return 'ios', True
        return '', False
    except:
        PrintException("Determining Upload type")