def start_avd():
    try:
        if platform.system() == 'Darwin':
            # There is a strage error in mac with the dyld one in a while..
            # this should fix it..
            if 'DYLD_FALLBACK_LIBRARY_PATH' in list(os.environ.keys()):
                del os.environ['DYLD_FALLBACK_LIBRARY_PATH']

        args = [
            settings.AVD_EMULATOR,
            '-avd',
            settings.AVD_NAME,
            "-writable-system",
            "-no-snapshot-load",
            "-port",
            str(settings.AVD_ADB_PORT),
        ]
        logger.info("starting emulator: \r\n" + ' '.join(args))
        subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except:
        PrintException("start_avd")
        return False