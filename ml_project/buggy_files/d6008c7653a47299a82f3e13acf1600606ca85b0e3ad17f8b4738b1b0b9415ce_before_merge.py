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
            sys.stderr.write("hyc: Can't open file '%s': [Errno %d] %s\n" %
                             (x.filename, x.errno, x.strerror))
            sys.exit(x.errno)