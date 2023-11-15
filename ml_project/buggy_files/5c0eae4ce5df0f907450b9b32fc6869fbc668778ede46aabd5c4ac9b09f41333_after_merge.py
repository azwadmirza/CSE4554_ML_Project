def dex_2_smali(app_dir, tools_dir):
    """Run dex2smali."""
    try:
        logger.info('DEX -> SMALI')
        dexes = get_dex_files(app_dir)
        for dex_path in dexes:
            logger.info('Converting %s to Smali Code',
                        filename_from_path(dex_path))
            if (len(settings.BACKSMALI_BINARY) > 0
                    and is_file_exists(settings.BACKSMALI_BINARY)):
                bs_path = settings.BACKSMALI_BINARY
            else:
                bs_path = os.path.join(tools_dir, 'baksmali-2.4.0.jar')
            output = os.path.join(app_dir, 'smali_source/')
            smali = [
                find_java_binary(),
                '-jar',
                bs_path,
                'd',
                dex_path,
                '-o',
                output,
            ]
            trd = threading.Thread(target=subprocess.call, args=(smali,))
            trd.daemon = True
            trd.start()
    except Exception:
        logger.exception('Converting DEX to SMALI')