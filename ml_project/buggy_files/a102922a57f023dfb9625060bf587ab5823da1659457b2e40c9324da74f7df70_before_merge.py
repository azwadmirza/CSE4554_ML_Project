def main(argv=sys.argv[1:]):
    # type: (List[str]) -> int
    """Parse and check the command line arguments."""
    locale.setlocale(locale.LC_ALL, '')
    sphinx.locale.init_console(os.path.join(package_dir, 'locale'), 'sphinx')

    parser = get_parser()
    args = parser.parse_args(argv)

    rootpath = path.abspath(args.module_path)

    # normalize opts

    if args.header is None:
        args.header = rootpath.split(path.sep)[-1]
    if args.suffix.startswith('.'):
        args.suffix = args.suffix[1:]
    if not path.isdir(rootpath):
        print(__('%s is not a directory.') % rootpath, file=sys.stderr)
        sys.exit(1)
    if not args.dryrun:
        ensuredir(args.destdir)
    excludes = [path.abspath(exclude) for exclude in args.exclude_pattern]
    modules = recurse_tree(rootpath, excludes, args)

    if args.full:
        from sphinx.cmd import quickstart as qs
        modules.sort()
        prev_module = ''  # type: unicode
        text = ''
        for module in modules:
            if module.startswith(prev_module + '.'):
                continue
            prev_module = module
            text += '   %s\n' % module
        d = dict(
            path = args.destdir,
            sep = False,
            dot = '_',
            project = args.header,
            author = args.author or 'Author',
            version = args.version or '',
            release = args.release or args.version or '',
            suffix = '.' + args.suffix,
            master = 'index',
            epub = True,
            extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode',
                          'sphinx.ext.todo'],
            makefile = True,
            batchfile = True,
            make_mode = True,
            mastertocmaxdepth = args.maxdepth,
            mastertoctree = text,
            language = 'en',
            module_path = rootpath,
            append_syspath = args.append_syspath,
        )
        if args.extensions:
            d['extensions'].extend(args.extensions)

        if isinstance(args.header, binary_type):
            d['project'] = d['project'].decode('utf-8')
        if isinstance(args.author, binary_type):
            d['author'] = d['author'].decode('utf-8')
        if isinstance(args.version, binary_type):
            d['version'] = d['version'].decode('utf-8')
        if isinstance(args.release, binary_type):
            d['release'] = d['release'].decode('utf-8')

        if not args.dryrun:
            qs.generate(d, silent=True, overwrite=args.force)
    elif args.tocfile:
        create_modules_toc_file(modules, args, args.tocfile)

    return 0