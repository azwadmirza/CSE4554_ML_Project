def run_code():
    # Add current directory to path, like Python itself does for -c.
    sys.path.insert(0, str(""))
    code = compile(options.target, str("<string>"), str("exec"))

    start_debugging(str("-c"))

    log.describe_environment("Pre-launch environment:")
    log.info("Running code:\n\n{0}", options.target)

    eval(code, {})