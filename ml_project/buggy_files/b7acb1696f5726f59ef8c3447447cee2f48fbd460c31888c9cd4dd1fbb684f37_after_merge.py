def get_identifier():
    """Get Device Type"""
    try:
        if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_REAL_DEVICE":
            return settings.DEVICE_IP + ":" + str(settings.DEVICE_ADB_PORT)
        elif settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
            return 'emulator-' + str(settings.AVD_ADB_PORT)
        else:
            return settings.VM_IP + ":" + str(settings.VM_ADB_PORT)
    except:
        PrintException(
            "Getting ADB Connection Identifier for Device/VM")