def sort_imports(
    file_name: str,
    config: Config,
    check: bool = False,
    ask_to_apply: bool = False,
    write_to_stdout: bool = False,
    **kwargs: Any,
) -> Optional[SortAttempt]:
    incorrectly_sorted: bool = False
    skipped: bool = False
    try:
        if check:
            try:
                incorrectly_sorted = not api.check_file(file_name, config=config, **kwargs)
            except FileSkipped:
                skipped = True
            return SortAttempt(incorrectly_sorted, skipped, True)

        try:
            incorrectly_sorted = not api.sort_file(
                file_name,
                config=config,
                ask_to_apply=ask_to_apply,
                write_to_stdout=write_to_stdout,
                **kwargs,
            )
        except FileSkipped:
            skipped = True
        return SortAttempt(incorrectly_sorted, skipped, True)
    except (OSError, ValueError) as error:
        warn(f"Unable to parse file {file_name} due to {error}")
        return None
    except UnsupportedEncoding:
        if config.verbose:
            warn(f"Encoding not supported for {file_name}")
        return SortAttempt(incorrectly_sorted, skipped, False)
    except KeyError as error:
        if error.args[0] not in DEFAULT_CONFIG.sections:
            _print_hard_fail(config, offending_file=file_name)
            raise
        msg = (
            f"Found {error} imports while parsing, but {error} was not included "
            "in the `sections` setting of your config. Please add it before continuing\n"
            "See https://pycqa.github.io/isort/#custom-sections-and-ordering "
            "for more info."
        )
        _print_hard_fail(config, message=msg)
        sys.exit(os.EX_CONFIG)
    except Exception:
        _print_hard_fail(config, offending_file=file_name)
        raise