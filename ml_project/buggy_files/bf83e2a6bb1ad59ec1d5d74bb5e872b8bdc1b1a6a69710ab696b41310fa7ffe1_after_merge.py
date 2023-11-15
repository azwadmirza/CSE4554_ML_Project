def handle_and_check(args):
    parsed = parse_args(args)
    profiler_enabled = False

    if parsed.record_timing_info:
        profiler_enabled = True

    with dbt.profiler.profiler(
        enable=profiler_enabled,
        outfile=parsed.record_timing_info
    ):

        initialize_config_values(parsed)

        reset_adapters()

        try:
            task, res = run_from_args(parsed)
        finally:
            dbt.tracking.flush()

        success = task.interpret_results(res)

        return res, success