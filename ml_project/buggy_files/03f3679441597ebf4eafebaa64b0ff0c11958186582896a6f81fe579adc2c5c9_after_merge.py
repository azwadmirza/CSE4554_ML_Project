def getADB():
    """Get ADB binary path"""
    try:
        if len(settings.ADB_BINARY) > 0 and isFileExists(settings.ADB_BINARY):
            return settings.ADB_BINARY
        else:
            adb = 'adb'
            if platform.system() == "Darwin":
                adb_dir = os.path.join(settings.TOOLS_DIR, 'adb/mac/')
                subprocess.call(["chmod", "777", adb_dir])
                adb = os.path.join(settings.TOOLS_DIR, 'adb/mac/adb')
            elif platform.system() == "Linux":
                adb_dir = os.path.join(settings.TOOLS_DIR, 'adb/linux/')
                subprocess.call(["chmod", "777", adb_dir])
                adb = os.path.join(settings.TOOLS_DIR, 'adb/linux/adb')
            elif platform.system() == "Windows":
                adb = os.path.join(settings.TOOLS_DIR, 'adb/windows/adb.exe')
            return adb
    except:
        PrintException("Getting ADB Location")
        return "adb"