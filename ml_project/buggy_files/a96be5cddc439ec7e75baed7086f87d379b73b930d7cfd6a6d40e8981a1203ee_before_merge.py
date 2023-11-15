def parse_args(detector_classes, printer_classes):
    parser = argparse.ArgumentParser(description='Slither. For usage information, see https://github.com/crytic/slither/wiki/Usage',
                                     usage="slither.py contract.sol [flag]")

    parser.add_argument('filename',
                        help='contract.sol')

    cryticparser.init(parser)

    parser.add_argument('--version',
                        help='displays the current version',
                        version=require('slither-analyzer')[0].version,
                        action='version')

    group_detector = parser.add_argument_group('Detectors')
    group_printer = parser.add_argument_group('Printers')
    group_misc = parser.add_argument_group('Additional option')

    group_detector.add_argument('--detect',
                                help='Comma-separated list of detectors, defaults to all, '
                                     'available detectors: {}'.format(
                                         ', '.join(d.ARGUMENT for d in detector_classes)),
                                action='store',
                                dest='detectors_to_run',
                                default=defaults_flag_in_config['detectors_to_run'])

    group_printer.add_argument('--print',
                               help='Comma-separated list fo contract information printers, '
                                    'available printers: {}'.format(
                                        ', '.join(d.ARGUMENT for d in printer_classes)),
                               action='store',
                               dest='printers_to_run',
                               default=defaults_flag_in_config['printers_to_run'])

    group_detector.add_argument('--list-detectors',
                                help='List available detectors',
                                action=ListDetectors,
                                nargs=0,
                                default=False)

    group_printer.add_argument('--list-printers',
                               help='List available printers',
                               action=ListPrinters,
                               nargs=0,
                               default=False)

    group_detector.add_argument('--exclude',
                                help='Comma-separated list of detectors that should be excluded',
                                action='store',
                                dest='detectors_to_exclude',
                                default=defaults_flag_in_config['detectors_to_exclude'])

    group_detector.add_argument('--exclude-informational',
                                help='Exclude informational impact analyses',
                                action='store_true',
                                default=defaults_flag_in_config['exclude_informational'])

    group_detector.add_argument('--exclude-low',
                                help='Exclude low impact analyses',
                                action='store_true',
                                default=defaults_flag_in_config['exclude_low'])

    group_detector.add_argument('--exclude-medium',
                                help='Exclude medium impact analyses',
                                action='store_true',
                                default=defaults_flag_in_config['exclude_medium'])

    group_detector.add_argument('--exclude-high',
                                help='Exclude high impact analyses',
                                action='store_true',
                                default=defaults_flag_in_config['exclude_high'])


    group_misc.add_argument('--json',
                            help='Export results as JSON',
                            action='store',
                            default=defaults_flag_in_config['json'])


    group_misc.add_argument('--disable-color',
                            help='Disable output colorization',
                            action='store_true',
                            default=defaults_flag_in_config['disable_color'])

    group_misc.add_argument('--filter-paths',
                            help='Comma-separated list of paths for which results will be excluded',
                            action='store',
                            dest='filter_paths',
                            default=defaults_flag_in_config['filter_paths'])

    group_misc.add_argument('--triage-mode',
                            help='Run triage mode (save results in slither.db.json)',
                            action='store_true',
                            dest='triage_mode',
                            default=False)

    group_misc.add_argument('--config-file',
                            help='Provide a config file (default: slither.config.json)',
                            action='store',
                            dest='config_file',
                            default='slither.config.json')

    # debugger command
    parser.add_argument('--debug',
                        help=argparse.SUPPRESS,
                        action="store_true",
                        default=False)

    parser.add_argument('--markdown',
                        help=argparse.SUPPRESS,
                        action=OutputMarkdown,
                        default=False)


    group_misc.add_argument('--checklist',
                            help=argparse.SUPPRESS,
                            action='store_true',
                            default=False)

    parser.add_argument('--wiki-detectors',
                        help=argparse.SUPPRESS,
                        action=OutputWiki,
                        default=False)

    parser.add_argument('--list-detectors-json',
                        help=argparse.SUPPRESS,
                        action=ListDetectorsJson,
                        nargs=0,
                        default=False)

    parser.add_argument('--legacy-ast',
                        help=argparse.SUPPRESS,
                        action='store_true',
                        default=defaults_flag_in_config['legacy_ast'])

    parser.add_argument('--ignore-return-value',
                        help=argparse.SUPPRESS,
                        action='store_true',
                        default=False)

    # if the json is splitted in different files
    parser.add_argument('--splitted',
                        help=argparse.SUPPRESS,
                        action='store_true',
                        default=False)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if os.path.isfile(args.config_file):
        try:
            with open(args.config_file) as f:
                config = json.load(f)
                for key, elem in config.items():
                    if key not in defaults_flag_in_config:
                        logger.info(yellow('{} has an unknown key: {} : {}'.format(args.config_file, key, elem)))
                        continue
                    if getattr(args, key) == defaults_flag_in_config[key]:
                        setattr(args, key, elem)
        except json.decoder.JSONDecodeError as e:
            logger.error(red('Impossible to read {}, please check the file {}'.format(args.config_file, e)))

    return args