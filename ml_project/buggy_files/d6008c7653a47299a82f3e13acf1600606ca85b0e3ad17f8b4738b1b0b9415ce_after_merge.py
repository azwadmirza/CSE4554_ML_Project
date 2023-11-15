def hyc_main():
    from hy.importer import write_hy_as_pyc
    parser = argparse.ArgumentParser(prog="hyc")
    parser.add_argument("files", metavar="FILE", nargs='+',
                        help="file to compile")
    parser.add_argument("-v", action="version", version=VERSION)

    options = parser.parse_args(sys.argv[1:])

    for file in options.files:
        try:
            print("Compiling %s" % file)
            pretty_error(write_hy_as_pyc, file)
        except IOError as x:
            print("hyc: Can't open file '{0}': [Errno {1}] {2}\n".format(
                x.filename, x.errno, x.strerror), file=sys.stderr)
            sys.exit(x.errno)