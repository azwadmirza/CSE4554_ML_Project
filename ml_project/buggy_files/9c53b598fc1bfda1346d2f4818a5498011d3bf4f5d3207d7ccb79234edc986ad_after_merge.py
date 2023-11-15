def main():
    """CLI Entrypoint"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    apply_parser = subparsers.add_parser(
        'apply', help='Applies patches (in GNU Quilt format) to the specified source tree')
    apply_parser.add_argument(
        '--patch-bin', help='The GNU patch command to use. Omit to find it automatically.')
    apply_parser.add_argument('target', type=Path, help='The directory tree to apply patches onto.')
    apply_parser.add_argument(
        'patches',
        type=Path,
        nargs='+',
        help='The directories containing patches to apply. They must be in GNU quilt format')
    apply_parser.set_defaults(callback=_apply_callback)

    merge_parser = subparsers.add_parser(
        'merge', help='Merges patches directories in GNU quilt format')
    merge_parser.add_argument(
        '--prepend',
        '-p',
        action='store_true',
        help=('If "destination" exists, prepend patches from sources into it.'
              ' By default, merging will fail if the destination already exists.'))
    merge_parser.add_argument(
        'destination',
        type=Path,
        help=('The directory to write the merged patches to. '
              'The destination must not exist unless --prepend is specified.'))
    merge_parser.add_argument(
        'source', type=Path, nargs='+', help='The GNU quilt patches to merge.')
    merge_parser.set_defaults(callback=_merge_callback)

    args = parser.parse_args()
    args.callback(args)