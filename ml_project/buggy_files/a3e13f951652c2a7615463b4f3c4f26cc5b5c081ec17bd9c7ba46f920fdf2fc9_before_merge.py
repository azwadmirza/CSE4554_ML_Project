def _apply_callback(args):
    logger = get_logger()
    for patch_dir in args.patches:
        logger.info('Applying patches from %s', patch_dir)
        apply_patches(
            generate_patches_from_series(patch_dir, resolve=True),
            args.directory,
            patch_bin_path=args.patch_bin)