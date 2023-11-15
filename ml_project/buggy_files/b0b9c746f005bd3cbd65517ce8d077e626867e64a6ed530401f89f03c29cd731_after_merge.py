def main():
    """Main entry point for Glances.

    Select the mode (standalone, client or server)
    Run it...
    """
    # Log Glances and PSutil version
    logger.info('Start Glances {}'.format(__version__))
    logger.info('{} {} and PSutil {} detected'.format(
        platform.python_implementation(),
        platform.python_version(),
        psutil_version))

    # Share global var
    global core

    # Create the Glances main instance
    core = GlancesMain()
    config = core.get_config()
    args = core.get_args()

    # Catch the CTRL-C signal
    signal.signal(signal.SIGINT, __signal_handler)

    # Glances can be ran in standalone, client or server mode
    if core.is_standalone()and not WINDOWS:
        start_standalone(config=config, args=args)
    elif core.is_client() and not WINDOWS:
        if core.is_client_browser():
            start_clientbrowser(config=config, args=args)
        else:
            start_client(config=config, args=args)
    elif core.is_server():
        start_server(config=config, args=args)
    elif core.is_webserver():
        # Web server mode replace the standalone mode on Windows OS
        start_webserver(config=config, args=args)