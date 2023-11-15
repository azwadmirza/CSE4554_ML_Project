def start_avd_from_snapshot():
    """Start AVD"""
    logger.info("Starting MobSF Emulator")
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
            "-snapshot",
            settings.AVD_SNAPSHOT,
            "-netspeed",
            "full",
            "-netdelay",
            "none",
            "-port",
            str(settings.AVD_ADB_PORT),
        ]
        subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Give a few seconds and check if the snapshot load succeed
        time.sleep(5)
        result = adb_command(["getprop", "init.svc.bootanim"], True)

        if result:
            if result.strip() == b"stopped":
                return True

        # Snapshot failed, stop the avd and return an error
        adb_command(["emu", "kill"])
        return False
    except:
        PrintException("Starting MobSF Emulator")
        return False