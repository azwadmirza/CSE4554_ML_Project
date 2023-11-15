def parse_args():
    parser = OptionParser("usage: %s [options] path1 path2" % sys.argv[0], description=desc, version=__version__)
    parser.add_option("-c", "--comment", dest="comment", default="", help="comment")
    parser.add_option("--src", dest="src", metavar="SOURCE_URL", default="http://openlibrary.org/", help="URL of the source server (default: %default)")
    parser.add_option("--dest", dest="dest", metavar="DEST_URL", default="http://localhost", help="URL of the destination server (default: %default)")
    parser.add_option("-r", "--recursive", dest="recursive", action='store_true', default=True, help="Recursively fetch all the referred docs.")
    parser.add_option("-l", "--list", dest="lists", action="append", default=[], help="copy docs from a list.")
    return parser.parse_args()