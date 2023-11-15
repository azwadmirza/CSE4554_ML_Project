def parse_options():
    parser = optparse.OptionParser(
        version='Mopidy %s' % versioning.get_version())
    parser.add_option(
        '-q', '--quiet',
        action='store_const', const=0, dest='verbosity_level',
        help='less output (warning level)')
    parser.add_option(
        '-v', '--verbose',
        action='count', default=1, dest='verbosity_level',
        help='more output (debug level)')
    return parser.parse_args(args=mopidy_args)[0]