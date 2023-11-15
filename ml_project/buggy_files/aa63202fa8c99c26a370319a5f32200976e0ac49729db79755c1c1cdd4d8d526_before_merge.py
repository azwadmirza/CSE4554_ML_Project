def help_boot_avd():
    try:
        emulator = get_identifier()

        # Wait for the adb to answer
        args = [settings.ADB_BINARY,
                "-s",
                emulator,
                "wait-for-device"]
        logger.info("help_boot_avd: wait-for-device")
        subprocess.call(args)

        # Make sure adb running as root
        logger.info("help_boot_avd: root")
        adb_command(['root'])

        # Make sure adb running as root
        logger.info("help_boot_avd: remount")
        adb_command(['remount'])

        # Make sure the system verity feature is disabled (Obviously, modified the system partition)
        logger.info("help_boot_avd: disable-verity")
        adb_command(['disable-verity'])

        # Make SELinux permissive - in case SuperSu/Xposed didn't patch things right
        logger.info("help_boot_avd: setenforce")
        adb_command(['setenforce', '0'], shell=True)

        logger.info("help_boot_avd: finished!")
        return True
    except:
        PrintException("[ERROR] help_boot_avd")
        return False