def main():
    from optparse import OptionParser

    p = OptionParser(description="conda link tool used by installer")

    p.add_option('--file',
                 action="store",
                 help="path of a file containing distributions to link, "
                      "by default all packages extracted in the cache are "
                      "linked")

    p.add_option('--prefix',
                 action="store",
                 default=sys.prefix,
                 help="prefix (defaults to %default)")

    p.add_option('-v', '--verbose',
                 action="store_true")

    if sys.platform == "win32":
        p.add_argument(
            "--shortcuts",
            action="store_true",
            help="Install start menu shortcuts"
        )

    opts, args = p.parse_args()
    if args:
        p.error('no arguments expected')

    logging.basicConfig()

    prefix = opts.prefix
    pkgs_dir = join(prefix, 'pkgs')
    pkgs_dirs[0] = [pkgs_dir]
    if opts.verbose:
        print("prefix: %r" % prefix)

    if opts.file:
        idists = list(yield_lines(join(prefix, opts.file)))
    else:
        idists = sorted(extracted())

    linktype = (LINK_HARD
                if idists and try_hard_link(pkgs_dir, prefix, idists[0]) else
                LINK_COPY)
    if opts.verbose:
        print("linktype: %s" % link_name_map[linktype])

    for dist in idists:
        if opts.verbose:
            print("linking: %s" % dist)
        link(prefix, dist, linktype, opts.shortcuts)

    messages(prefix)

    for dist in duplicates_to_remove(linked(prefix), idists):
        meta_path = join(prefix, 'conda-meta', dist + '.json')
        print("WARNING: unlinking: %s" % meta_path)
        try:
            os.rename(meta_path, meta_path + '.bak')
        except OSError:
            rm_rf(meta_path)