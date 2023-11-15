def process_gcov_data(data_fname, covdata, source_fname, options):
    logger = Logger(options.verbose)

    INPUT = open(data_fname, "r")

    # Find the source file
    firstline = INPUT.readline()
    fname = guess_source_file_name(
        firstline, data_fname, source_fname,
        root_dir=options.root_dir, starting_dir=options.starting_dir,
        logger=logger)

    logger.verbose_msg("Parsing coverage data for file {}", fname)

    # Return if the filename does not match the filter
    # Return if the filename matches the exclude pattern
    filtered, excluded = apply_filter_include_exclude(
        fname, options.filter, options.exclude, strip=options.root_filter)

    if filtered:
        logger.verbose_msg("  Filtering coverage data for file {}", fname)
        return

    if excluded:
        logger.verbose_msg("  Excluding coverage data for file {}", fname)
        return

    parser = GcovParser(fname, logger=logger)
    parser.parse_all_lines(INPUT, options.exclude_unreachable_branches)
    parser.update_coverage(covdata)
    parser.check_unrecognized_lines()
    parser.check_unclosed_exclusions()

    INPUT.close()