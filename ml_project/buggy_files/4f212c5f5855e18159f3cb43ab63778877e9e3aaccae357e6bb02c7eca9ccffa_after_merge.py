def run_file():
    target = options.target
    start_debugging(target)

    target_as_str = compat.filename_str(target)

    # run_path has one difference with invoking Python from command-line:
    # if the target is a file (rather than a directory), it does not add its
    # parent directory to sys.path. Thus, importing other modules from the
    # same directory is broken unless sys.path is patched here.

    if os.path.isfile(target_as_str):
        dir = os.path.dirname(target_as_str)
        sys.path.insert(0, dir)
    else:
        log.debug("Not a file: {0!r}", target)

    log.describe_environment("Pre-launch environment:")

    log.info("Running file {0!r}", target)
    runpy.run_path(target_as_str, run_name=compat.force_str("__main__"))