def main():
    """ CLI entry point """
    args = parse_args()
    cppname = "libopenage"
    cppdir = Path(cppname).absolute()
    out_cppdir = Path(args.output_dir) / cppname

    if args.verbose:
        hdr_count = len(args.all_files)
        plural = "s" if hdr_count > 1 else ""

        print("extracting pxd information "
              "from {} header{}...".format(hdr_count, plural))

    for filename in args.all_files:
        filename = Path(filename).resolve()
        if cppdir not in filename.parents:
            print("pxdgen source file is not in " + cppdir + ": " + filename)
            sys.exit(1)

        # join out_cppdir with relative path from cppdir
        pxdfile_relpath = filename.with_suffix('.pxd').relative_to(cppdir)
        pxdfile = out_cppdir / pxdfile_relpath

        if args.verbose:
            print("creating '{}' for '{}':".format(pxdfile, filename))

        generator = PXDGenerator(filename)

        result = generator.generate(
            pxdfile,
            ignore_timestamps=args.ignore_timestamps,
            print_warnings=True
        )

        if args.verbose and not result:
            print("nothing done.")

        # create empty __init__.py in all parent directories.
        # Cython requires this; else it won't find the .pxd files.
        for dirname in pxdfile_relpath.parents:
            template = out_cppdir / dirname / "__init__"
            for extension in ("py", "pxd"):
                initfile = template.with_suffix("." + extension)
                if not initfile.exists():
                    print("\x1b[36mpxdgen: create package index %s\x1b[0m" % (
                        initfile.relative_to(CWD)))

                    initfile.touch()