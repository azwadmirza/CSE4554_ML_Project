def main():
    """CLI Entrypoint"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--downloads-cache',
        type=Path,
        metavar='PATH',
        default='../../downloads_cache',
        help='The path to the downloads cache')
    parser.add_argument(
        '--disable-ssl-verification',
        action='store_true',
        help='Disables SSL verification for downloading')
    parser.add_argument(
        '--7z-path',
        dest='sevenz_path',
        default=SEVENZIP_USE_REGISTRY,
        help=('Command or path to 7-Zip\'s "7z" binary. If "_use_registry" is '
              'specified, determine the path from the registry. Default: %(default)s'))
    args = parser.parse_args()

    # Set common variables
    bundle_path = Path(__file__).parent / 'config_bundles/windows'
    bundle = buildkit.config.ConfigBundle(bundle_path)
    source_tree = Path(__file__).resolve().parent.parent
    domsubcache = Path(__file__).parent / 'domsubcache.tar.gz'

    # Test environment
    _test_python2(parser.error)

    # Setup environment
    if not args.downloads_cache.exists():
        args.downloads_cache.mkdir()
    _make_tmp_paths()

    # Retrieve downloads
    get_logger().info('Downloading required files...')
    buildkit.downloads.retrieve_downloads(bundle, args.downloads_cache, True,
                                          args.disable_ssl_verification)
    try:
        buildkit.downloads.check_downloads(bundle, args.downloads_cache)
    except buildkit.downloads.HashMismatchError as exc:
        get_logger().error('File checksum does not match: %s', exc)
        parser.exit(1)

    # Unpack downloads
    extractors = {
        ExtractorEnum.SEVENZIP: args.sevenz_path,
    }
    get_logger().info('Unpacking downloads...')
    buildkit.downloads.unpack_downloads(bundle, args.downloads_cache, source_tree, extractors)

    # Prune binaries
    unremovable_files = buildkit.extraction.prune_dir(source_tree, bundle.pruning)
    if unremovable_files:
        get_logger().error('Files could not be pruned: %s', unremovable_files)
        parser.exit(1)

    # Apply patches
    buildkit.patches.apply_patches(
        buildkit.patches.patch_paths_by_bundle(bundle), source_tree, patch_bin_path=None)

    # Substitute domains
    buildkit.domain_substitution.apply_substitution(bundle, source_tree, domsubcache)

    # Output args.gn
    (source_tree / 'out/Default').mkdir(parents=True)
    (source_tree / 'out/Default/args.gn').write_text('\n'.join(bundle.gn_flags), encoding=ENCODING)

    # Run GN bootstrap
    _run_build_process(
        shutil.which('python'), 'tools\\gn\\bootstrap\\bootstrap.py', '-o'
        'out\\Default\\gn.exe')

    # Run gn gen
    _run_build_process('out\\Default\\gn.exe', 'gen', 'out\\Default', '--fail-on-unused-args')

    # Run ninja
    _run_build_process('third_party\\ninja\\ninja.exe', '-C', 'out\\Default', 'chrome',
                       'chromedriver')