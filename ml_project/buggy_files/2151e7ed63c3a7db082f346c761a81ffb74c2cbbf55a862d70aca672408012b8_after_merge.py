def _report_options(p):
    """ Add options specific to the report subcommand. """
    _default_options(p, blacklist=['cache', 'log-group', 'quiet'])
    p.add_argument(
        '--days', type=float, default=1,
        help="Number of days of history to consider")
    p.add_argument(
        '--raw', type=argparse.FileType('w'),
        help="Store raw json of collected records to given file path")
    p.add_argument(
        '--field', action='append', default=[], type=_key_val_pair,
        metavar='HEADER=FIELD',
        help='Repeatable. JMESPath of field to include in the output OR '
        'for a tag use prefix `tag:`. Special case fields `region` and'
        '`policy` are available')
    p.add_argument(
        '--no-default-fields', action="store_true",
        help='Exclude default fields for report.')
    p.add_argument(
        '--format', default='csv', choices=['csv', 'grid', 'simple', 'json'],
        help="Format to output data in (default: %(default)s). "
        "Options include simple, grid, csv, json")