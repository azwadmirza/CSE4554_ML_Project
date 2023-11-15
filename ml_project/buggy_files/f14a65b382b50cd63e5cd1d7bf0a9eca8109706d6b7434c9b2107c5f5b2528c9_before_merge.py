def create_parser():
    parser = argparse.ArgumentParser(
        prog='download_mapping',
        description='Downloads malware family mapping and converts it to modify syntax.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
You can specify additional rules to be added to the file by using:
-e "^some-expression$" -i "some-identifier"
and multiple ones:
-e "^some-expression$" -i "some-identifier" -e "^other-expression$" -i "other-identifier"
'''
    )

    parser.add_argument('filename', nargs='?',
                        help='The filename to write the converted mapping to. If not given, printed to stdout.')
    parser.add_argument('--url', '-u',
                        default=URL,
                        help='The URL to download the mapping from.')
    parser.add_argument('--add-default', '-d',
                        help='Add a default rule to use the malware name as identifier.',
                        const=True, action='store_const')
    parser.add_argument('--expression', '-e',
                        nargs=1, action='append',
                        help='Expression for an additional rule.')
    parser.add_argument('--identifier', '-i',
                        nargs=1, action='append',
                        help='Identifier for an additional rule.')
    parser.add_argument('-m', '--include-malpedia',
                        default=False, action='store_true',
                        help='Include malpedia data (CC BY-NC-SA 3.0), '
                             'see https://malpedia.caad.fkie.fraunhofer.de/usage/tos from %s'
                             '' % URL_MALPEDIA)
    return parser