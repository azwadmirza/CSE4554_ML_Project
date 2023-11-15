def _apply_callback(args, parser_error):
    logger = get_logger()
    patch_bin_path = None
    if args.patch_bin is not None:
        patch_bin_path = Path(args.patch_bin)
        if not patch_bin_path.exists():
            patch_bin_path = shutil.which(args.patch_bin)
            if patch_bin_path:
                patch_bin_path = Path(patch_bin_path)
            else:
                parser_error(
                    f'--patch-bin "{args.patch_bin}" is not a command or path to executable.')
    for patch_dir in args.patches:
        logger.info('Applying patches from %s', patch_dir)
        apply_patches(
            generate_patches_from_series(patch_dir, resolve=True),
            args.target,
            patch_bin_path=args.patch_bin)