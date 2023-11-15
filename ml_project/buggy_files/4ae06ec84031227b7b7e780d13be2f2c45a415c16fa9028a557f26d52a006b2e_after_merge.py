def diy(self, args):
    if not args.spec:
        tty.die("spack diy requires a package spec argument.")

    specs = spack.cmd.parse_specs(args.spec)
    if len(specs) > 1:
        tty.die("spack diy only takes one spec.")

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
            "spack diy spec must have a single, concrete version. "
            "Did you forget a package version number?")

    spec.concretize()
    package = spack.repo.get(spec)

    if package.installed:
        tty.error("Already installed in %s" % package.prefix)
        tty.msg("Uninstall or try adding a version suffix for this DIY build.")
        sys.exit(1)

    # Forces the build to run out of the current directory.
    package.stage = DIYStage(os.getcwd())

    # TODO: make this an argument, not a global.
    spack.do_checksum = False

    package.do_install(
        keep_prefix=args.keep_prefix,
        install_deps=not args.ignore_deps,
        verbose=not args.quiet,
        keep_stage=True,   # don't remove source dir for DIY.
        dirty=args.dirty)