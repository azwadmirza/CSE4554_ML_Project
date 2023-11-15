def graph(parser, args):
    concretize = not args.normalize
    if args.installed:
        if args.specs:
            tty.die("Can't specify specs with --installed")
        args.dot = True
        specs = spack.installed_db.query()

    else:
        specs = spack.cmd.parse_specs(
            args.specs, normalize=True, concretize=concretize)

    if not specs:
        setup_parser.parser.print_help()
        return 1

    deptype = nobuild
    if args.deptype:
        deptype = tuple(args.deptype.split(','))
        validate_deptype(deptype)
        deptype = canonical_deptype(deptype)

    if args.dot:  # Dot graph only if asked for.
        graph_dot(specs, static=args.static, deptype=deptype)

    elif specs:  # ascii is default: user doesn't need to provide it explicitly
        graph_ascii(specs[0], debug=spack.debug, deptype=deptype)
        for spec in specs[1:]:
            print  # extra line bt/w independent graphs
            graph_ascii(spec, debug=spack.debug)