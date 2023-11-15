def handle_and_check(args):
    parsed = parse_args(args)
    profiler_enabled = False

    if parsed.record_timing_info:
        profiler_enabled = True

    with dbt.profiler.profiler(
        enable=profiler_enabled,
        outfile=parsed.record_timing_info
    ):
        # this needs to happen after args are parsed so we can determine the
        # correct profiles.yml file
        profile_config = read_config(parsed.profiles_dir)
        if not send_anonymous_usage_stats(profile_config):
            dbt.tracking.do_not_track()
        else:
            dbt.tracking.initialize_tracking()

        if colorize_output(profile_config):
            dbt.ui.printer.use_colors()

        reset_adapters()

        try:
            task, res = run_from_args(parsed)
        finally:
            dbt.tracking.flush()

        success = task.interpret_results(res)

        return res, success