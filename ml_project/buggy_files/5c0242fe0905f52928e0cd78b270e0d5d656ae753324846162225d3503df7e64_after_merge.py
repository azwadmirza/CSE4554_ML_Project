def dex_2_smali(app_dir, tools_dir):
    """Run dex2smali"""
    try:
        logger.info("DEX -> SMALI")
        dexes = get_dex_files(app_dir)
        for dex_path in dexes:
            logger.info("Converting " + dex_path + " to Smali Code")
            if len(settings.BACKSMALI_BINARY) > 0 and isFileExists(settings.BACKSMALI_BINARY):
                bs_path = settings.BACKSMALI_BINARY
            else:
                bs_path = os.path.join(tools_dir, 'baksmali.jar')
            output = os.path.join(app_dir, 'smali_source/')
            args = [
                settings.JAVA_PATH + 'java',
                '-jar', bs_path, dex_path, '-o', output
            ]
            subprocess.call(args)
    except:
        PrintException("Converting DEX to SMALI")