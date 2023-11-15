def run_module():
    # Add current directory to path, like Python itself does for -m. This must
    # be in place before trying to use find_spec below to resolve submodules.
    sys.path.insert(0, str(""))

    # We want to do the same thing that run_module() would do here, without
    # actually invoking it. On Python 3, it's exposed as a public API, but
    # on Python 2, we have to invoke a private function in runpy for this.
    # Either way, if it fails to resolve for any reason, just leave argv as is.
    argv_0 = sys.argv[0]
    target_as_str = compat.filename_str(options.target)
    try:
        if sys.version_info >= (3,):
            from importlib.util import find_spec

            spec = find_spec(target_as_str)
            if spec is not None:
                argv_0 = spec.origin
        else:
            _, _, _, argv_0 = runpy._get_module_details(target_as_str)
    except Exception:
        log.swallow_exception("Error determining module path for sys.argv")

    start_debugging(argv_0)

    # On Python 2, module name must be a non-Unicode string, because it ends up
    # a part of module's __package__, and Python will refuse to run the module
    # if __package__ is Unicode.

    log.describe_environment("Pre-launch environment:")
    log.info("Running module {0!r}", options.target)

    # Docs say that runpy.run_module is equivalent to -m, but it's not actually
    # the case for packages - -m sets __name__ to "__main__", but run_module sets
    # it to "pkg.__main__". This breaks everything that uses the standard pattern
    # __name__ == "__main__" to detect being run as a CLI app. On the other hand,
    # runpy._run_module_as_main is a private function that actually implements -m.
    try:
        run_module_as_main = runpy._run_module_as_main
    except AttributeError:
        log.warning("runpy._run_module_as_main is missing, falling back to run_module.")
        runpy.run_module(target_as_str, alter_sys=True)
    else:
        run_module_as_main(target_as_str, alter_argv=True)