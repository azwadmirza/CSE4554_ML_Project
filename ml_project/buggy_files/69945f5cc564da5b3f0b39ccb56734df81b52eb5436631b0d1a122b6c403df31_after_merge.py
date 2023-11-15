def main(argv=sys.argv[1:]):
    # type: (List[str]) -> None
    sphinx.locale.setlocale(locale.LC_ALL, '')
    sphinx.locale.init_console(os.path.join(package_dir, 'locale'), 'sphinx')

    app = DummyApplication()
    setup_documenters(app)
    args = get_parser().parse_args(argv)
    generate_autosummary_docs(args.source_file, args.output_dir,
                              '.' + args.suffix,
                              template_dir=args.templates,
                              imported_members=args.imported_members,
                              app=app)