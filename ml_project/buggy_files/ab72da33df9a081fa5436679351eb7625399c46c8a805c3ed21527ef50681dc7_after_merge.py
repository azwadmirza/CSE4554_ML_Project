def main():
    args = _options.options.parse_args()

    if args.help:
        _options.options.print_help()
        return

    if args.version:
        print(metadata.version("nox"), file=sys.stderr)
        return

    setup_logging(color=args.color, verbose=args.verbose)

    # Execute the appropriate tasks.
    exit_code = workflow.execute(
        global_config=args,
        workflow=(
            tasks.load_nox_module,
            tasks.merge_noxfile_options,
            tasks.discover_manifest,
            tasks.filter_manifest,
            tasks.honor_list_request,
            tasks.verify_manifest_nonempty,
            tasks.run_manifest,
            tasks.print_summary,
            tasks.create_report,
            tasks.final_reduce,
        ),
    )

    # Done; exit.
    sys.exit(exit_code)