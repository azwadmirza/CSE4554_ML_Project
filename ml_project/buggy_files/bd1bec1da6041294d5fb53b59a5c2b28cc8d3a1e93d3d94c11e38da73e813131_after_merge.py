def salt_cloud():
    '''
    The main function for salt-cloud
    '''
    if '' in sys.path:
        sys.path.remove('')

    if not HAS_SALTCLOUD:
        print('salt-cloud is not available in this system')
        sys.exit(1)

    try:
        salt.cloud.libcloudfuncs.check_libcloud_version()
    except ImportError as exc:
        print(exc)
        sys.exit(1)

    try:
        cloud = salt.cloud.cli.SaltCloud()
        cloud.run()
    except KeyboardInterrupt:
        raise SystemExit('\nExiting gracefully on Ctrl-c')