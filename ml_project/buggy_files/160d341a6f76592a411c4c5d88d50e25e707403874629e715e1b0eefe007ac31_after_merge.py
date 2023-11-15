def check_basic_env():
    """Check if we have basic env for MobSF to run."""
    logger.info('MobSF Basic Environment Check')
    try:
        import http_tools  # noqa F401
    except ImportError:
        logger.exception('httptools not installed!')
        os.kill(os.getpid(), signal.SIGTERM)
    try:
        import lxml  # noqa F401
    except ImportError:
        logger.exception('lxml is not installed!')
        os.kill(os.getpid(), signal.SIGTERM)
    if not is_file_exists(find_java_binary()):
        logger.error(
            'JDK 8+ is not available. '
            'Set JAVA_HOME environment variable'
            ' or JAVA_DIRECTORY in MobSF/settings.py')
        logger.info('Current Configuration: '
                    'JAVA_DIRECTORY=%s', settings.JAVA_DIRECTORY)
        logger.info('Example Configuration:'
                    '\nJAVA_DIRECTORY = "C:/Program Files/'
                    'Java/jdk1.7.0_17/bin/"'
                    '\nJAVA_DIRECTORY = "/usr/bin/"')
        os.kill(os.getpid(), signal.SIGTERM)
    get_adb()