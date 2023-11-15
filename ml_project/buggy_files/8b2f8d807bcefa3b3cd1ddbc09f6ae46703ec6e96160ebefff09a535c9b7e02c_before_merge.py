def run():
    args = parse_args()

    # if hosts are not specified, either parse from hostfile, or default as
    # localhost
    if not args.hosts:
        if args.hostfile:
            args.hosts = parse_host_files(args.hostfile)
        else:
            # Set hosts to localhost if not specified
            args.hosts = 'localhost:{np}'.format(np=args.np)

    host_list = args.hosts.split(',')
    all_host_names = []
    pattern = re.compile(r'^[\w-]+:\d+$')
    for host in host_list:
        if not pattern.match(host.strip()):
            raise ValueError('Invalid host input, please make sure it has '
                             'format as : worker-0:2,worker-1:2.')
        all_host_names.append(host.strip().split(':')[0])

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
                                     key=secret.make_secret_key(),
                                     timeout=tmout,
                                     num_hosts=len(all_host_names),
                                     num_proc=args.np,
                                     hosts=args.hosts,
                                     command=args.command)

    # This cache stores the results of checks performed by horovodrun
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

    if len(remote_host_names) > 0:
        if settings.verbose >= 2:
            print('Testing interfaces on all the hosts.')

        local_host_names = set(all_host_names) - set(remote_host_names)
        # Find the set of common, routed interfaces on all the hosts (remote
        # and local) and specify it in the args to be used by NCCL. It is
        # expected that the following function will find at least one interface
        # otherwise, it will raise an exception.
        common_intfs = _driver_fn(all_host_names, local_host_names,
                                  settings, fn_cache=fn_cache)

        if settings.verbose >= 2:
            print('Interfaces on all the hosts were successfully checked.')
            print('Common interface found: ' + ' '.join(common_intfs))

    else:
        if settings.verbose >= 2:
            print('All hosts are local, finding the interfaces '
                  'with address 127.0.0.1')
        # If all the given hosts are local, find the interfaces with address
        # 127.0.0.1
        common_intfs = set()
        for iface, addrs in net_if_addrs().items():
            for addr in addrs:
                if addr.family == AF_INET and addr.address == '127.0.0.1':
                    common_intfs.add(iface)
                    break

        if len(common_intfs) == 0:
            raise ValueError('No interface is found for address 127.0.0.1.')

        if settings.verbose >= 2:
            print('Local interface found ' + ' '.join(common_intfs))

    if args.use_gloo:
        if not gloo_built():
            raise ValueError('Gloo support has not been built.  If this is not expected, ensure CMake is installed '
                             'and reinstall Horovod with HOROVOD_WITH_GLOO=1 to debug the build error.')
        gloo_run(settings, remote_host_names, common_intfs)
    elif args.use_mpi:
        if not mpi_built():
            raise ValueError('MPI support has not been built.  If this is not expected, ensure MPI is installed '
                             'and reinstall Horovod with HOROVOD_WITH_MPI=1 to debug the build error.')
        mpi_run(settings, common_intfs)
    else:
        if mpi_built():
            mpi_run(settings, common_intfs)
        elif gloo_built():
            gloo_run(settings, remote_host_names, common_intfs)
        else:
            raise ValueError('Neither MPI nor Gloo support has been built. Try reinstalling Horovod ensuring that '
                             'either MPI is installed (MPI) or CMake is installed (Gloo).')