def run_file():
    start_debugging(options.target)

    # run_path has one difference with invoking Python from command-line:
    # if the target is a file (rather than a directory), it does not add its
    # parent directory to sys.path. Thus, importing other modules from the
    # same directory is broken unless sys.path is patched here.
    if os.path.isfile(options.target):
        dir = os.path.dirname(options.target)
        sys.path.insert(0, dir)
    else:
        log.debug("Not a file: {0!r}", options.target)

    log.describe_environment("Pre-launch environment:")
    log.info("Running file {0!r}", options.target)

    runpy.run_path(options.target, run_name=compat.force_str("__main__"))