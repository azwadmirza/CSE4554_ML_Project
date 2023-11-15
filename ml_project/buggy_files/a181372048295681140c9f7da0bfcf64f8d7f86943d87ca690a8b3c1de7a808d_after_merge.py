def setup(self, args):
    if not args.spec:
        tty.die("spack setup requires a package spec argument.")

    specs = spack.cmd.parse_specs(args.spec)
    if len(specs) > 1:
        tty.die("spack setup only takes one spec.")

    # Take a write lock before checking for existence.
    with spack.store.db.write_transaction():
        spec = specs[0]
        if not spack.repo.exists(spec.name):
            tty.warn("No such package: %s" % spec.name)
            create = tty.get_yes_or_no("Create this package?", default=False)
            if not create:
                tty.msg("Exiting without creating.")
                sys.exit(1)
            else:
                tty.msg("Running 'spack edit -f %s'" % spec.name)
                edit_package(spec.name, spack.repo.first_repo(), None, True)
                return

        if not spec.versions.concrete:
            tty.die(
                "spack setup spec must have a single, concrete version. "
                "Did you forget a package version number?")

        spec.concretize()
        package = spack.repo.get(spec)
        if not isinstance(package, spack.CMakePackage):
            tty.die(
                'Support for {0} derived packages not yet implemented'.format(
                    package.build_system_class
                )
            )

        # It's OK if the package is already installed.

        # Forces the build to run out of the current directory.
        package.stage = DIYStage(os.getcwd())

        # TODO: make this an argument, not a global.
        spack.do_checksum = False

        # Install dependencies if requested to do so
        if not args.ignore_deps:
            parser = argparse.ArgumentParser()
            install.setup_parser(parser)
            inst_args = copy.deepcopy(args)
            inst_args = parser.parse_args(
                ['--only=dependencies'] + args.spec,
                namespace=inst_args
            )
            install.install(parser, inst_args)
        # Generate spconfig.py
        tty.msg(
            'Generating spconfig.py [{0}]'.format(package.spec.cshort_spec)
        )
        write_spconfig(package)
        # Install this package to register it in the DB and permit
        # module file regeneration
        inst_args = copy.deepcopy(args)
        inst_args = parser.parse_args(
            ['--only=package', '--fake'] + args.spec,
            namespace=inst_args
        )
        install.install(parser, inst_args)