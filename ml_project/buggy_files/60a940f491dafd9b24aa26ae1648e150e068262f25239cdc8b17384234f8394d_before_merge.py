def check_parallel(linter, jobs, files, arguments=None):
    """Use the given linter to lint the files with given amount of workers (jobs)"""
    # The reporter does not need to be passed to worker processess, i.e. the reporter does
    # not need to be pickleable
    original_reporter = linter.reporter
    linter.reporter = None

    # The linter is inherited by all the pool's workers, i.e. the linter
    # is identical to the linter object here. This is requred so that
    # a custom PyLinter object can be used.
    initializer = functools.partial(_worker_initialize, arguments=arguments)
    with multiprocessing.Pool(jobs, initializer=initializer, initargs=[linter]) as pool:
        # ..and now when the workers have inherited the linter, the actual reporter
        # can be set back here on the parent process so that results get stored into
        # correct reporter
        linter.set_reporter(original_reporter)
        linter.open()

        all_stats = []

        for module, base_name, messages, stats, msg_status in pool.imap_unordered(
            _worker_check_single_file, files
        ):
            linter.file_state.base_name = base_name
            linter.set_current_module(module)
            for msg in messages:
                msg = Message(*msg)
                linter.reporter.handle_message(msg)

            all_stats.append(stats)
            linter.msg_status |= msg_status

    linter.stats = _merge_stats(all_stats)

    # Insert stats data to local checkers.
    for checker in linter.get_checkers():
        if checker is not linter:
            checker.stats = linter.stats