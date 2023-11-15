def install_and_run(apk_path, package, launcher, is_activity):
    """Install APK and Run it"""
    logger.info("Starting App for Dynamic Analysis")
    try:
        adb = getADB()
        logger.info("Installing APK")
        adb_command(["install", "-r", apk_path])
        if is_activity:
            run_app = package + "/" + launcher
            logger.info("Launching APK Main Activity")
            adb_command(["am", "start", "-n", run_app], True)
        else:
            logger.info("App Doesn't have a Main Activity")
            # Handle Service or Give Choice to Select in Future.
        logger.info("Testing Environment is Ready!")
    except:
        PrintException("Starting App for Dynamic Analysis")