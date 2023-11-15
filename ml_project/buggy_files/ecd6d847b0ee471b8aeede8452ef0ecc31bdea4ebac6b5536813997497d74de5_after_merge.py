def install(parser, args, **kwargs):
    if not args.package:
        tty.die("install requires at least one package argument")

    if args.jobs is not None:
        if args.jobs <= 0:
            tty.die("The -j option must be a positive integer!")

    if args.no_checksum:
        spack.do_checksum = False        # TODO: remove this global.

    # Parse cli arguments and construct a dictionary
    # that will be passed to Package.do_install API
    kwargs.update({
        'keep_prefix': args.keep_prefix,
        'keep_stage': args.keep_stage,
        'restage': args.restage,
        'install_deps': 'dependencies' in args.things_to_install,
        'make_jobs': args.jobs,
        'run_tests': args.run_tests,
        'verbose': args.verbose,
        'fake': args.fake,
        'dirty': args.dirty
    })

    # Spec from cli
    specs = spack.cmd.parse_specs(args.package, concretize=True)
    if len(specs) == 0:
        tty.error('The `spack install` command requires a spec to install.')

    for spec in specs:
        # Check if we were asked to produce some log for dashboards
        if args.log_format is not None:
            # Compute the filename for logging
            log_filename = args.log_file
            if not log_filename:
                log_filename = default_log_file(spec)
            # Create the test suite in which to log results
            test_suite = TestSuite(spec)
            # Decorate PackageBase.do_install to get installation status
            PackageBase.do_install = junit_output(
                spec, test_suite
            )(PackageBase.do_install)

        # Do the actual installation
        if args.things_to_install == 'dependencies':
            # Install dependencies as-if they were installed
            # for root (explicit=False in the DB)
            kwargs['explicit'] = False
            for s in spec.dependencies():
                p = spack.repo.get(s)
                p.do_install(**kwargs)
        else:
            package = spack.repo.get(spec)
            kwargs['explicit'] = True
            package.do_install(**kwargs)

        # Dump log file if asked to
        if args.log_format is not None:
            test_suite.dump(log_filename)