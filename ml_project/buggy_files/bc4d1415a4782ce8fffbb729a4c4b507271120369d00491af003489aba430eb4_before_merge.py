def plot_parse_args(args ):
    parser = common_args_parser(args, 'Graph utility')
    parser.add_argument(
        '-p', '--pair',
        help = 'What currency pair',
        dest = 'pair',
        default = 'BTC_ETH',
        type = str,
    )
    return parser.parse_args(args)