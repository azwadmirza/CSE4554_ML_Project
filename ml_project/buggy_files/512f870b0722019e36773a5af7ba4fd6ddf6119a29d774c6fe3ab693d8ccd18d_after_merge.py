def connect():
    """Connect to VM/Device"""
    logger.info("Connecting to VM/Device")
    adb = getADB()
    subprocess.call([adb, "kill-server"])
    subprocess.call([adb, "start-server"])
    logger.info("ADB Started")
    wait(5)
    logger.info("Connecting to VM/Device")
    out = subprocess.check_output([adb, "connect", get_identifier()])
    if b"unable to connect" in out:
        raise ValueError("ERROR Connecting to VM/Device. ",
                         out.decode("utf-8").replace("\n", ""))
    try:
        subprocess.call([adb, "-s", get_identifier(), "wait-for-device"])
        logger.info("Mounting")
        if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_REAL_DEVICE":
            adb_command(["su", "-c", "mount", "-o",
                         "rw,remount,rw", "/system"], True)
        else:
            adb_command(["su", "-c", "mount", "-o",
                         "rw,remount,rw", "/system"], True)
            # This may not work for VMs other than the default MobSF VM
            adb_command(["mount", "-o", "rw,remount", "-t", "rfs",
                         "/dev/block/sda6", "/system"], True)
    except:
        PrintException("Connecting to VM/Device")