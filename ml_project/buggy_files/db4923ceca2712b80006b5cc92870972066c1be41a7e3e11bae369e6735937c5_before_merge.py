def refresh_avd():
    """Refresh AVD"""

    # Before we load the AVD, check paths
    for path in [settings.AVD_EMULATOR,
                 settings.ADB_BINARY]:
        if not path:
            logger.error("AVD binaries not configured, please refer to the official documentation")
            return False

    logger.info("Refreshing MobSF Emulator")
    try:
        # Stop existing emulator
        stop_avd()

        # Check if configuration specifies cold or warm boot
        if settings.AVD_COLD_BOOT:
            if start_avd_cold():
                logger.info("AVD has been started successfully")
                return True
        else:
            if not settings.AVD_SNAPSHOT:
                logger.error("AVD not configured properly - AVD_SNAPSHOT is missing")
                return False
            if start_avd_from_snapshot():
                logger.info("AVD has been loaded from snapshot successfully")
                return True
        return False

    except:
        PrintException("[ERROR] Refreshing MobSF VM")
        return False