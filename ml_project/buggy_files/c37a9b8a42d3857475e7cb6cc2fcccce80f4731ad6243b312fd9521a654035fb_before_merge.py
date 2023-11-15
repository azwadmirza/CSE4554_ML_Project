def main(argv: List[str] = sys.argv[1:]) -> None:
    sphinx.locale.setlocale(locale.LC_ALL, '')
    sphinx.locale.init_console(os.path.join(package_dir, 'locale'), 'sphinx')

    app = DummyApplication()
    logging.setup(app, sys.stdout, sys.stderr)  # type: ignore
    setup_documenters(app)
    args = get_parser().parse_args(argv)
    builder = DummyBuilder(app, args.templates)
    generate_autosummary_docs(args.source_file, args.output_dir,
                              '.' + args.suffix, builder=builder,  # type: ignore
                              imported_members=args.imported_members,
                              app=app)