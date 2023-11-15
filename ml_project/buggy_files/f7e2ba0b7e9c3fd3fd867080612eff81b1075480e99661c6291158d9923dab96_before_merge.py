def process_options(args: List[str],
                    require_targets: bool = True
                    ) -> Tuple[List[BuildSource], Options]:
    """Parse command line arguments."""

    # Make the help output a little less jarring.
    help_factory = (lambda prog:
                    argparse.RawDescriptionHelpFormatter(prog=prog, max_help_position=28))
    parser = argparse.ArgumentParser(prog='mypy', epilog=FOOTER,
                                     fromfile_prefix_chars='@',
                                     formatter_class=help_factory)

    # Unless otherwise specified, arguments will be parsed directly onto an
    # Options object.  Options that require further processing should have
    # their `dest` prefixed with `special-opts:`, which will cause them to be
    # parsed into the separate special_opts namespace object.
    parser.add_argument('-v', '--verbose', action='count', dest='verbosity',
                        help="more verbose messages")
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('--python-version', type=parse_version, metavar='x.y',
                        help='use Python x.y')
    parser.add_argument('--platform', action='store', metavar='PLATFORM',
                        help="typecheck special-cased code for the given OS platform "
                        "(defaults to sys.platform).")
    parser.add_argument('-2', '--py2', dest='python_version', action='store_const',
                        const=defaults.PYTHON2_VERSION, help="use Python 2 mode")
    parser.add_argument('-s', '--silent-imports', action='store_true',
                        help="don't follow imports to .py files")
    parser.add_argument('--almost-silent', action='store_true',
                        help="like --silent-imports but reports the imports as errors")
    parser.add_argument('--disallow-untyped-calls', action='store_true',
                        help="disallow calling functions without type annotations"
                        " from functions with type annotations")
    parser.add_argument('--disallow-untyped-defs', action='store_true',
                        help="disallow defining functions without type annotations"
                        " or with incomplete type annotations")
    parser.add_argument('--check-untyped-defs', action='store_true',
                        help="type check the interior of functions without type annotations")
    parser.add_argument('--disallow-subclassing-any', action='store_true',
                        help="disallow subclassing values of type 'Any' when defining classes")
    parser.add_argument('--warn-incomplete-stub', action='store_true',
                        help="warn if missing type annotation in typeshed, only relevant with"
                        " --check-untyped-defs enabled")
    parser.add_argument('--warn-redundant-casts', action='store_true',
                        help="warn about casting an expression to its inferred type")
    parser.add_argument('--warn-unused-ignores', action='store_true',
                        help="warn about unneeded '# type: ignore' comments")
    parser.add_argument('--hide-error-context', action='store_true',
                        dest='hide_error_context',
                        help="Hide context notes before errors")
    parser.add_argument('--fast-parser', action='store_true',
                        help="enable experimental fast parser")
    parser.add_argument('-i', '--incremental', action='store_true',
                        help="enable experimental module cache")
    parser.add_argument('--cache-dir', action='store', metavar='DIR',
                        help="store module cache info in the given folder in incremental mode "
                        "(defaults to '{}')".format(defaults.CACHE_DIR))
    parser.add_argument('--strict-optional', action='store_true',
                        dest='strict_optional',
                        help="enable experimental strict Optional checks")
    parser.add_argument('--strict-optional-whitelist', metavar='GLOB', nargs='*',
                        help="suppress strict Optional errors in all but the provided files "
                        "(experimental -- read documentation before using!).  "
                        "Implies --strict-optional.  Has the undesirable side-effect of "
                        "suppressing other errors in non-whitelisted files.")
    parser.add_argument('--pdb', action='store_true', help="invoke pdb on fatal error")
    parser.add_argument('--show-traceback', '--tb', action='store_true',
                        help="show traceback on fatal error")
    parser.add_argument('--stats', action='store_true', dest='dump_type_stats', help="dump stats")
    parser.add_argument('--inferstats', action='store_true', dest='dump_inference_stats',
                        help="dump type inference stats")
    parser.add_argument('--custom-typing', metavar='MODULE', dest='custom_typing_module',
                        help="use a custom typing module")
    parser.add_argument('--scripts-are-modules', action='store_true',
                        help="Script x becomes module x instead of __main__")
    parser.add_argument('--config-file',
                        help="Configuration file, must have a [mypy] section "
                        "(defaults to {})".format(defaults.CONFIG_FILE))
    parser.add_argument('--show-column-numbers', action='store_true',
                        dest='show_column_numbers',
                        help="Show column numbers in error messages")
    # hidden options
    # --shadow-file a.py tmp.py will typecheck tmp.py in place of a.py.
    # Useful for tools to make transformations to a file to get more
    # information from a mypy run without having to change the file in-place
    # (e.g. by adding a call to reveal_type).
    parser.add_argument('--shadow-file', metavar='PATH', nargs=2, dest='shadow_file',
                        help=argparse.SUPPRESS)
    # --debug-cache will disable any cache-related compressions/optimizations,
    # which will make the cache writing process output pretty-printed JSON (which
    # is easier to debug).
    parser.add_argument('--debug-cache', action='store_true', help=argparse.SUPPRESS)
    # deprecated options
    parser.add_argument('--silent', action='store_true', dest='special-opts:silent',
                        help=argparse.SUPPRESS)
    parser.add_argument('-f', '--dirty-stubs', action='store_true',
                        dest='special-opts:dirty_stubs',
                        help=argparse.SUPPRESS)
    parser.add_argument('--use-python-path', action='store_true',
                        dest='special-opts:use_python_path',
                        help=argparse.SUPPRESS)

    report_group = parser.add_argument_group(
        title='report generation',
        description='Generate a report in the specified format.')
    for report_type in sorted(reporter_classes):
        report_group.add_argument('--%s-report' % report_type.replace('_', '-'),
                                  metavar='DIR',
                                  dest='special-opts:%s_report' % report_type)

    code_group = parser.add_argument_group(title='How to specify the code to type check')
    code_group.add_argument('-m', '--module', action='append', metavar='MODULE',
                            dest='special-opts:modules',
                            help="type-check module; can repeat for more modules")
    # TODO: `mypy -p A -p B` currently silently ignores ignores A
    # (last option wins).  Perhaps -c, -m and -p could just be
    # command-line flags that modify how we interpret self.files?
    code_group.add_argument('-c', '--command', action='append', metavar='PROGRAM_TEXT',
                            dest='special-opts:command',
                            help="type-check program passed in as string")
    code_group.add_argument('-p', '--package', metavar='PACKAGE', dest='special-opts:package',
                            help="type-check all files in a directory")
    code_group.add_argument(metavar='files', nargs='*', dest='special-opts:files',
                            help="type-check given files or directories")

    # Parse arguments once into a dummy namespace so we can get the
    # filename for the config file.
    dummy = argparse.Namespace()
    parser.parse_args(args, dummy)
    config_file = dummy.config_file or defaults.CONFIG_FILE

    # Parse config file first, so command line can override.
    options = Options()
    if config_file and os.path.exists(config_file):
        parse_config_file(options, config_file)

    # Parse command line for real, using a split namespace.
    special_opts = argparse.Namespace()
    parser.parse_args(args, SplitNamespace(options, special_opts, 'special-opts:'))

    # --use-python-path is no longer supported; explain why.
    if special_opts.use_python_path:
        parser.error("Sorry, --use-python-path is no longer supported.\n"
                     "If you are trying this because your code depends on a library module,\n"
                     "you should really investigate how to obtain stubs for that module.\n"
                     "See https://github.com/python/mypy/issues/1411 for more discussion."
                     )

    # warn about deprecated options
    if special_opts.silent:
        print("Warning: --silent is deprecated; use --silent-imports",
              file=sys.stderr)
        options.silent_imports = True
    if special_opts.dirty_stubs:
        print("Warning: -f/--dirty-stubs is deprecated and no longer necessary. Mypy no longer "
              "checks the git status of stubs.",
              file=sys.stderr)

    # Check for invalid argument combinations.
    if require_targets:
        code_methods = sum(bool(c) for c in [special_opts.modules,
                                            special_opts.command,
                                            special_opts.package,
                                            special_opts.files])
        if code_methods == 0:
            parser.error("Missing target module, package, files, or command.")
        elif code_methods > 1:
            parser.error("May only specify one of: module, package, files, or command.")

    # Set build flags.
    if options.strict_optional_whitelist is not None:
        # TODO: Deprecate, then kill this flag
        options.strict_optional = True
    if options.strict_optional:
        experiments.STRICT_OPTIONAL = True

    # Set reports.
    for flag, val in vars(special_opts).items():
        if flag.endswith('_report') and val is not None:
            report_type = flag[:-7].replace('_', '-')
            report_dir = val
            options.report_dirs[report_type] = report_dir

    # Set target.
    if special_opts.modules:
        options.build_type = BuildType.MODULE
        targets = [BuildSource(None, m, None) for m in special_opts.modules]
        return targets, options
    elif special_opts.package:
        if os.sep in special_opts.package or os.altsep and os.altsep in special_opts.package:
            fail("Package name '{}' cannot have a slash in it."
                 .format(special_opts.package))
        options.build_type = BuildType.MODULE
        lib_path = [os.getcwd()] + build.mypy_path()
        targets = build.find_modules_recursive(special_opts.package, lib_path)
        if not targets:
            fail("Can't find package '{}'".format(special_opts.package))
        return targets, options
    elif special_opts.command:
        options.build_type = BuildType.PROGRAM_TEXT
        return [BuildSource(None, None, '\n'.join(special_opts.command))], options
    else:
        targets = []
        for f in special_opts.files:
            if f.endswith(PY_EXTENSIONS):
                targets.append(BuildSource(f, crawl_up(f)[1], None))
            elif os.path.isdir(f):
                sub_targets = expand_dir(f)
                if not sub_targets:
                    fail("There are no .py[i] files in directory '{}'"
                         .format(f))
                targets.extend(sub_targets)
            else:
                mod = os.path.basename(f) if options.scripts_are_modules else None
                targets.append(BuildSource(f, mod, None))
        return targets, options