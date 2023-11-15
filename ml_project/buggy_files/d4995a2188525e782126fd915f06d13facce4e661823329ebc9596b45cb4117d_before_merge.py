def install(parser, args):
    if not args.packages:
        tty.die("install requires at least one package argument")

    if args.jobs is not None:
        if args.jobs <= 0:
            tty.die("The -j option must be a positive integer!")

    if args.no_checksum:
        spack.do_checksum = False        # TODO: remove this global.

    specs = spack.cmd.parse_specs(args.packages, concretize=True)
    for spec in specs:
        package = spack.repo.get(spec)
        with spack.installed_db.write_transaction():
            package.do_install(
                keep_prefix=args.keep_prefix,
                keep_stage=args.keep_stage,
                install_deps=not args.ignore_deps,
                install_self=not args.deps_only,
                make_jobs=args.jobs,
                run_tests=args.run_tests,
                verbose=args.verbose,
                fake=args.fake,
                dirty=args.dirty,
                explicit=True)