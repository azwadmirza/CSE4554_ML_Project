def _run_static(args):
    all_host_names, _ = parse_hosts_and_slots(args.hosts)

    nics_set = set(args.nics.split(',')) if args.nics else None

    # horovodrun has to finish all the checks before this timeout runs out.
    if args.start_timeout:
        start_timeout = args.start_timeout
    else:
        # Lookup default timeout from the environment variable.
        start_timeout = int(os.getenv('HOROVOD_START_TIMEOUT', '30'))

    tmout = timeout.Timeout(start_timeout,
                            message='Timed out waiting for {activity}. Please '
                                    'check connectivity between servers. You '
                                    'may need to increase the --start-timeout '
                                    'parameter if you have too many servers.')
    settings = hvd_settings.Settings(verbose=2 if args.verbose else 0,
                                     ssh_port=args.ssh_port,
                                     extra_mpi_args=args.mpi_args,
                                     tcp_flag=args.tcp_flag,
                                     binding_args=args.binding_args,
                                     key=secret.make_secret_key(),
                                     start_timeout=tmout,
                                     num_proc=args.np,
                                     hosts=args.hosts,
                                     num_hosts=len(all_host_names),
                                     output_filename=args.output_filename,
                                     run_func_mode=args.run_func is not None,
                                     nics=nics_set)

    # This cache stores the results of checks performed by horovod
    # during the initialization step. It can be disabled by setting
    # --disable-cache flag.
    fn_cache = None
    if not args.disable_cache:
        params = ''
        if args.np:
            params += str(args.np) + ' '
        if args.hosts:
            params += str(args.hosts) + ' '
        if args.ssh_port:
            params += str(args.ssh_port)
        parameters_hash = hashlib.md5(params.encode('utf-8')).hexdigest()
        fn_cache = cache.Cache(CACHE_FOLDER, CACHE_STALENESS_THRESHOLD_MINUTES,
                               parameters_hash)

    if settings.verbose >= 2:
        print('Filtering local host names.')
    remote_host_names = network.filter_local_addresses(all_host_names)
    if settings.verbose >= 2:
        print('Remote host found: ' + ' '.join(remote_host_names))

    if len(remote_host_names) > 0:
        if settings.verbose >= 2:
            print('Checking ssh on all remote hosts.')
        # Check if we can ssh into all remote hosts successfully.
        _check_all_hosts_ssh_successful(remote_host_names, args.ssh_port,
                                        fn_cache=fn_cache)
        if settings.verbose >= 2:
            print('SSH was successful into all the remote hosts.')

    nics = driver_service.get_common_interfaces(settings, all_host_names,
                                                remote_host_names, fn_cache)

    if args.run_func:
        # get the driver IPv4 address
        driver_ip = network.get_driver_ip(nics)
        run_func_server = KVStoreServer(verbose=settings.verbose)
        run_func_server_port = run_func_server.start_server()
        put_data_into_kvstore(driver_ip, run_func_server_port,
                              'runfunc', 'func', args.run_func)

        command = [sys.executable, '-m', 'horovod.run.run_task', str(driver_ip), str(run_func_server_port)]

        try:
            _launch_job(args, settings, nics, command)
            results = [None] * args.np
            # TODO: make it parallel to improve performance
            for i in range(args.np):
                results[i] = read_data_from_kvstore(driver_ip, run_func_server_port,
                                                    'runfunc_result', str(i))
            return results
        finally:
            run_func_server.shutdown_server()
    else:
        command = args.command
        _launch_job(args, settings, nics, command)
        return None