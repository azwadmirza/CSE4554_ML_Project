def check_basic_env():
    """Check if we have basic env for MobSF to run"""
    logger.info("MobSF Basic Environment Check")
    try:
        import capfuzz
    except ImportError:
        PrintException("CapFuzz not installed!")
        os.kill(os.getpid(), signal.SIGTERM)
    try:
        import lxml
    except ImportError:
        PrintException("lxml is not installed!")
        os.kill(os.getpid(), signal.SIGTERM)
    if platform.system() == "Windows":
        java = settings.JAVA_PATH + 'java.exe'
    else:
        java = settings.JAVA_PATH + 'java'
    if not isFileExists(java):
        logger.error(
            "Oracle Java is not available or `JAVA_DIRECTORY` in settings.py is configured incorrectly!")
        logger.info("JAVA_DIRECTORY=%s" % settings.JAVA_DIRECTORY)
        logger.info('''Example Configuration:
                 JAVA_DIRECTORY = "C:/Program Files/Java/jdk1.7.0_17/bin/"
                 JAVA_DIRECTORY = "/usr/bin/"
        ''')
        os.kill(os.getpid(), signal.SIGTERM)