def hy2py_main():
    import platform

    options = dict(prog="hy2py", usage="%(prog)s [options] [FILE]",
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    parser = argparse.ArgumentParser(**options)
    parser.add_argument("FILE", type=str, nargs='?',
                        help="Input Hy code (use STDIN if \"-\" or "
                             "not provided)")
    parser.add_argument("--with-source", "-s", action="store_true",
                        help="Show the parsed source structure")
    parser.add_argument("--with-ast", "-a", action="store_true",
                        help="Show the generated AST")
    parser.add_argument("--without-python", "-np", action="store_true",
                        help=("Do not show the Python code generated "
                              "from the AST"))

    options = parser.parse_args(sys.argv[1:])

    if options.FILE is None or options.FILE == '-':
        filename = '<stdin>'
        source = sys.stdin.read()
    else:
        filename = options.FILE
        with io.open(options.FILE, 'r', encoding='utf-8') as source_file:
            source = source_file.read()

    with filtered_hy_exceptions():
        hst = hy_parse(source, filename=filename)

    if options.with_source:
        # need special printing on Windows in case the
        # codepage doesn't support utf-8 characters
        if PY3 and platform.system() == "Windows":
            for h in hst:
                try:
                    print(h)
                except:
                    print(str(h).encode('utf-8'))
        else:
            print(hst)
        print()
        print()

    with filtered_hy_exceptions():
        _ast = hy_compile(hst, '__main__', filename=filename, source=source)

    if options.with_ast:
        if PY3 and platform.system() == "Windows":
            _print_for_windows(astor.dump_tree(_ast))
        else:
            print(astor.dump_tree(_ast))
        print()
        print()

    if not options.without_python:
        if PY3 and platform.system() == "Windows":
            _print_for_windows(astor.code_gen.to_source(_ast))
        else:
            print(astor.code_gen.to_source(_ast))

    parser.exit(0)