def stop_avd():
    """Stop AVD"""
    logger.info("Stopping MobSF Emulator")
    try:
        adb_command(['emu', 'kill'], silent=True)
    except:
        PrintException("[ERROR] Stopping MobSF Emulator")