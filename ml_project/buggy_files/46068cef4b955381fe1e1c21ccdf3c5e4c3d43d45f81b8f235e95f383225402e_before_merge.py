def check_config():
    try:
        for path in [settings.AVD_EMULATOR,
                     settings.ADB_BINARY]:
            if not path:
                logger.error("ADB binary not configured, please refer to the official documentation")
                return False
        if settings.ANDROID_DYNAMIC_ANALYZER != 'MobSF_AVD':
            logger.error("Wrong configuration - ANDROID_DYNAMIC_ANALYZER, please refer to the official documentation")
            return False
        return True
    except:
        PrintException("[ERROR] check_config")
        return False