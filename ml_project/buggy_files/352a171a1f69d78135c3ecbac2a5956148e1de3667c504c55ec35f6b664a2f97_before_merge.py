def main() -> None:
    options = parse_options(sys.argv[1:])
    if not os.path.isdir(options.output_dir):
        raise SystemExit('Directory "{}" does not exist'.format(options.output_dir))
    if options.recursive and options.no_import:
        raise SystemExit('recursive stub generation without importing is not currently supported')
    sigs = {}  # type: Any
    class_sigs = {}  # type: Any
    if options.doc_dir:
        all_sigs = []  # type: Any
        all_class_sigs = []  # type: Any
        for path in glob.glob('%s/*.rst' % options.doc_dir):
            with open(path) as f:
                func_sigs, class_sigs = parse_all_signatures(f.readlines())
            all_sigs += func_sigs
            all_class_sigs += class_sigs
        sigs = dict(find_unique_signatures(all_sigs))
        class_sigs = dict(find_unique_signatures(all_class_sigs))
    for module in (options.modules if not options.recursive else walk_packages(options.modules)):
        try:
            generate_stub_for_module(module,
                                     output_dir=options.output_dir,
                                     add_header=True,
                                     sigs=sigs,
                                     class_sigs=class_sigs,
                                     pyversion=options.pyversion,
                                     no_import=options.no_import,
                                     search_path=options.search_path,
                                     interpreter=options.interpreter,
                                     include_private=options.include_private)
        except Exception as e:
            if not options.ignore_errors:
                raise e
            else:
                print("Stub generation failed for", module, file=sys.stderr)