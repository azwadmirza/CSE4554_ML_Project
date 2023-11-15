def main():
    if USING_ARGPARSE:
        parser = argparse.ArgumentParser(
            description='Create views from nmap and passive databases.')
    else:
        parser = optparse.OptionParser(
            description='Create views from nmap and passive databases.')
        parser.parse_args_orig = parser.parse_args

        def my_parse_args():
            res = parser.parse_args_orig()
            res[0].ensure_value('ips', res[1])
            return res[0]
        parser.parse_args = my_parse_args
        parser.add_argument = parser.add_option

    fltnmap = db.nmap.flt_empty
    fltpass = db.passive.flt_empty
    _from = []

    parser.add_argument('--category', metavar='CATEGORY',
                        help='Choose a different category than the default')
    parser.add_argument('--test', '-t', action='store_true',
                        help='Give results in standard output instead of '
                             'inserting them in database.')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='For test output, print out formated results.')

    if not USING_ARGPARSE:
        if 'nmap' in sys.argv:
            for args, kargs in db.nmap.argparser.args:
                parser.add_option(*args, **kargs)
        elif 'passive' in sys.argv:
            for args, kargs in db.passive.argparser.args:
                parser.add_option(*args, **kargs)
        else:
            print('ivre db2view: error: invalid subcommand {nmap, passive}.')
            exit(-1)
    else:
        subparsers = parser.add_subparsers(dest='view_source',
                                           help="Accepted values are "
                                                "'nmap' and 'passive'")

        subparsers.add_parser('nmap', parents=[db.nmap.argparser])
        passparser = subparsers.add_parser('passive',
                                           parents=[db.passive.argparser])
        passparser.add_argument('ips', nargs='*')

    args = parser.parse_args()

    if args.category:
        db.view.category = args.category
    if not args.view_source:
        args.view_source = 'all'
    if args.view_source == 'all':
        fltnmap = db.nmap.parse_args(args)
        fltpass = db.passive.parse_args(args)
        _from = [from_nmap(fltnmap), from_passive(fltpass)]
    elif args.view_source == 'nmap':
        fltnmap = db.nmap.parse_args(args, fltnmap)
        _from = [from_nmap(fltnmap)]
    elif args.view_source == 'passive':
        fltpass = db.passive.parse_args(args, fltpass)
        _from = [from_passive(fltpass)]
    if args.test:

        def output(x):
            print(x)
    else:
        output = db.view.store_or_merge_host
    # Filter by ip for passive
    if args.view_source == 'passive' and args.ips:
        flt = db.passive.flt_empty
        for a in args.ips:
            if '-' in a:
                a = a.split('-', 1)
                if a[0].isdigit():
                    a[0] = int(a[0])
                if a[1].isdigit():
                    a[1] = int(a[1])
                flt = db.passive.flt_or(
                    flt, db.passive.searchrange(a[0], a[1])
                )
            elif '/' in a:
                flt = db.passive.flt_or(flt, db.passive.searchnet(a))
            else:
                if a.isdigit():
                    a = db.passive.ip2internal(int(a))
                flt = db.passive.flt_or(flt, db.passive.searchhost(a))
        fltpass = db.passive.flt_and(fltpass, flt)
    # Output results
    itr = to_view(_from)
    if not itr:
        return
    for elt in itr:
        output(elt)