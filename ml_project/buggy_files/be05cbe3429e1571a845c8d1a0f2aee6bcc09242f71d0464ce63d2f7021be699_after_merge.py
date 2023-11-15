def main(script_path: str) -> None:
    """Main entry point to the type checker.

    Args:
        script_path: Path to the 'mypy' script (used for finding data files).
    """
    t0 = time.time()
    if script_path:
        bin_dir = find_bin_directory(script_path)
    else:
        bin_dir = None
    sys.setrecursionlimit(2 ** 14)
    sources, options = process_options(sys.argv[1:])
    serious = False
    try:
        res = type_check_only(sources, bin_dir, options)
        a = res.errors
    except CompileError as e:
        a = e.messages
        if not e.use_stdout:
            serious = True
    if options.junit_xml:
        t1 = time.time()
        util.write_junit_xml(t1 - t0, serious, a, options.junit_xml)
    if a:
        f = sys.stderr if serious else sys.stdout
        try:
            for m in a:
                f.write(m + '\n')
        except BrokenPipeError:
            pass
        sys.exit(1)