def adb_binary_or32bit_support():
    """Check if 32bit is supported. Also if the binary works"""
    adb_path = getADB()
    try:
        fnull = open(os.devnull, 'w')
        subprocess.call([adb_path], stdout=fnull, stderr=fnull)
    except:
        msg = "\n[WARNING] You don't have 32 bit execution support enabled or MobSF shipped" \
            " ADB binary is not compatible with your OS."\
            "\nPlease set the 'ADB_BINARY' path in settings.py"
        if platform.system != "Windows":
            logger.warning(Color.BOLD + Color.ORANGE + msg + Color.END)
        else:
            logger.warning(msg)