def parse_options():
    parser = optparse.OptionParser(
        version='Mopidy %s' % versioning.get_version())
    # NOTE Python 2.6: To support Python versions < 2.6.2rc1 we must use
    # bytestrings for the first argument to ``add_option``
    # See https://github.com/mopidy/mopidy/issues/302 for details
    parser.add_option(
        b'-q', '--quiet',
        action='store_const', const=0, dest='verbosity_level',
        help='less output (warning level)')
    parser.add_option(
        b'-v', '--verbose',
        action='count', default=1, dest='verbosity_level',
        help='more output (debug level)')
    return parser.parse_args(args=mopidy_args)[0]