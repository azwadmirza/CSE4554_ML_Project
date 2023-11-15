def _build(sources: List[BuildSource],
           options: Options,
           alt_lib_path: Optional[str],
           bin_dir: Optional[str],
           flush_errors: Callable[[List[str], bool], None],
           fscache: Optional[FileSystemCache],
           ) -> BuildResult:
    # This seems the most reasonable place to tune garbage collection.
    gc.set_threshold(50000)

    data_dir = default_data_dir()
    fscache = fscache or FileSystemCache()

    search_paths = compute_search_paths(sources, options, data_dir, fscache, alt_lib_path)

    reports = Reports(data_dir, options.report_dirs)
    source_set = BuildSourceSet(sources)
    errors = Errors(options.show_error_context, options.show_column_numbers)
    plugin = load_plugins(options, errors)

    # Construct a build manager object to hold state during the build.
    #
    # Ignore current directory prefix in error messages.
    manager = BuildManager(data_dir, search_paths,
                           ignore_prefix=os.getcwd(),
                           source_set=source_set,
                           reports=reports,
                           options=options,
                           version_id=__version__,
                           plugin=plugin,
                           errors=errors,
                           flush_errors=flush_errors,
                           fscache=fscache)

    reset_global_state()
    try:
        graph = dispatch(sources, manager)
        if not options.fine_grained_incremental:
            TypeState.reset_all_subtype_caches()
        return BuildResult(manager, graph)
    finally:
        manager.log("Build finished in %.3f seconds with %d modules, and %d errors" %
                    (time.time() - manager.start_time,
                     len(manager.modules),
                     manager.errors.num_messages()))
        # Finish the HTML or XML reports even if CompileError was raised.
        reports.finish()