def main(script_path: Optional[str],
         stdout: TextIO,
         stderr: TextIO,
         args: Optional[List[str]] = None,
         ) -> None:
    """Main entry point to the type checker.

    Args:
        script_path: Path to the 'mypy' script (used for finding data files).
        args: Custom command-line arguments.  If not given, sys.argv[1:] will
        be used.
    """
    util.check_python_version('mypy')
    t0 = time.time()
    # To log stat() calls: os.stat = stat_proxy
    sys.setrecursionlimit(2 ** 14)
    if args is None:
        args = sys.argv[1:]

    fscache = FileSystemCache()
    sources, options = process_options(args, stdout=stdout, stderr=stderr,
                                       fscache=fscache)

    messages = []
    formatter = util.FancyFormatter(stdout, stderr, options.show_error_codes)

    def flush_errors(new_messages: List[str], serious: bool) -> None:
        if options.pretty:
            new_messages = formatter.fit_in_terminal(new_messages)
        messages.extend(new_messages)
        f = stderr if serious else stdout
        try:
            for msg in new_messages:
                if options.color_output:
                    msg = formatter.colorize(msg)
                f.write(msg + '\n')
            f.flush()
        except BrokenPipeError:
            sys.exit(2)

    serious = False
    blockers = False
    res = None
    try:
        # Keep a dummy reference (res) for memory profiling below, as otherwise
        # the result could be freed.
        res = build.build(sources, options, None, flush_errors, fscache, stdout, stderr)
    except CompileError as e:
        blockers = True
        if not e.use_stdout:
            serious = True
    if options.warn_unused_configs and options.unused_configs and not options.incremental:
        print("Warning: unused section(s) in %s: %s" %
              (options.config_file,
               ", ".join("[mypy-%s]" % glob for glob in options.per_module_options.keys()
                         if glob in options.unused_configs)),
              file=stderr)
    maybe_write_junit_xml(time.time() - t0, serious, messages, options)

    if MEM_PROFILE:
        from mypy.memprofile import print_memory_profile
        print_memory_profile()

    code = 0
    if messages:
        code = 2 if blockers else 1
    if options.error_summary:
        if messages:
            n_errors, n_files = util.count_stats(messages)
            if n_errors:
                stdout.write(formatter.format_error(n_errors, n_files, len(sources),
                                                    options.color_output) + '\n')
        else:
            stdout.write(formatter.format_success(len(sources),
                                                  options.color_output) + '\n')
        stdout.flush()
    if options.fast_exit:
        # Exit without freeing objects -- it's faster.
        #
        # NOTE: We don't flush all open files on exit (or run other destructors)!
        util.hard_exit(code)
    elif code:
        sys.exit(code)

    # HACK: keep res alive so that mypyc won't free it before the hard_exit
    list([res])