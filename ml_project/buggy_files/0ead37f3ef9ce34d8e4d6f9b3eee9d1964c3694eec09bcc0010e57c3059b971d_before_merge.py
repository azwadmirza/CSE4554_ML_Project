def get_command():

    def instance_remote_manager(client_cache):
        requester = requests.Session()
        requester.proxies = client_cache.conan_config.proxies
        # Verify client version against remotes
        version_checker_requester = VersionCheckerRequester(requester, Version(CLIENT_VERSION),
                                                            Version(MIN_SERVER_COMPATIBLE_VERSION),
                                                            out)
        # To handle remote connections
        rest_api_client = RestApiClient(out, requester=version_checker_requester)
        # To store user and token
        localdb = LocalDB(client_cache.localdb)
        # Wraps RestApiClient to add authentication support (same interface)
        auth_manager = ConanApiAuthManager(rest_api_client, user_io, localdb)
        # Handle remote connections
        remote_manager = RemoteManager(client_cache, auth_manager, out)
        return remote_manager

    use_color = get_env("CONAN_COLOR_DISPLAY", 1)
    if use_color and hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        import colorama
        colorama.init()
        color = True
    else:
        color = False
    out = ConanOutput(sys.stdout, color)
    user_io = UserIO(out=out)

    user_folder = os.getenv("CONAN_USER_HOME", conan_expand_user("~"))

    try:
        # To capture exceptions in conan.conf parsing
        client_cache = ClientCache(user_folder, None, out)
        # obtain a temp ConanManager instance to execute the migrations
        remote_manager = instance_remote_manager(client_cache)

        # Get a DiskSearchManager
        search_adapter = DiskSearchAdapter()
        search_manager = DiskSearchManager(client_cache, search_adapter)
        manager = ConanManager(client_cache, user_io, ConanRunner(), remote_manager, search_manager)

        client_cache = migrate_and_get_client_cache(user_folder, out, manager)
    except Exception as e:
        out.error(str(e))
        sys.exit(True)

    # Get the new command instance after migrations have been done
    remote_manager = instance_remote_manager(client_cache)

    # Get a search manager
    search_adapter = DiskSearchAdapter()
    search_manager = DiskSearchManager(client_cache, search_adapter)
    command = Command(client_cache, user_io, ConanRunner(), remote_manager, search_manager)
    return command