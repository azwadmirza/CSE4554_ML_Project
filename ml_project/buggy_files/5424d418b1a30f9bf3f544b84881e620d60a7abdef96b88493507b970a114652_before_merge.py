def parse_section(prefix: str, template: Options,
                  section: Mapping[str, str],
                  stderr: TextIO = sys.stderr
                  ) -> Tuple[Dict[str, object], Dict[str, str]]:
    """Parse one section of a config file.

    Returns a dict of option values encountered, and a dict of report directories.
    """
    results = {}  # type: Dict[str, object]
    report_dirs = {}  # type: Dict[str, str]
    for key in section:
        invert = False
        options_key = key
        if key in config_types:
            ct = config_types[key]
        else:
            dv = getattr(template, key, None)
            if dv is None:
                if key.endswith('_report'):
                    report_type = key[:-7].replace('_', '-')
                    if report_type in defaults.REPORTER_NAMES:
                        report_dirs[report_type] = section[key]
                    else:
                        print("%sUnrecognized report type: %s" % (prefix, key),
                              file=stderr)
                    continue
                if key.startswith('x_'):
                    pass  # Don't complain about `x_blah` flags
                elif key.startswith('no_') and hasattr(template, key[3:]):
                    options_key = key[3:]
                    invert = True
                elif key.startswith('allow') and hasattr(template, 'dis' + key):
                    options_key = 'dis' + key
                    invert = True
                elif key.startswith('disallow') and hasattr(template, key[3:]):
                    options_key = key[3:]
                    invert = True
                elif key == 'strict':
                    print("%sStrict mode is not supported in configuration files: specify "
                          "individual flags instead (see 'mypy -h' for the list of flags enabled "
                          "in strict mode)" % prefix, file=stderr)
                else:
                    print("%sUnrecognized option: %s = %s" % (prefix, key, section[key]),
                          file=stderr)
                if invert:
                    dv = getattr(template, options_key, None)
                else:
                    continue
            ct = type(dv)
        v = None  # type: Any
        try:
            if ct is bool:
                v = section.getboolean(key)  # type: ignore[attr-defined]  # Until better stub
                if invert:
                    v = not v
            elif callable(ct):
                if invert:
                    print("%sCan not invert non-boolean key %s" % (prefix, options_key),
                          file=stderr)
                    continue
                try:
                    v = ct(section.get(key))
                except argparse.ArgumentTypeError as err:
                    print("%s%s: %s" % (prefix, key, err), file=stderr)
                    continue
            else:
                print("%sDon't know what type %s should have" % (prefix, key), file=stderr)
                continue
        except ValueError as err:
            print("%s%s: %s" % (prefix, key, err), file=stderr)
            continue
        if key == 'silent_imports':
            print("%ssilent_imports has been replaced by "
                  "ignore_missing_imports=True; follow_imports=skip" % prefix, file=stderr)
            if v:
                if 'ignore_missing_imports' not in results:
                    results['ignore_missing_imports'] = True
                if 'follow_imports' not in results:
                    results['follow_imports'] = 'skip'
        if key == 'almost_silent':
            print("%salmost_silent has been replaced by "
                  "follow_imports=error" % prefix, file=stderr)
            if v:
                if 'follow_imports' not in results:
                    results['follow_imports'] = 'error'
        results[options_key] = v
    return results, report_dirs