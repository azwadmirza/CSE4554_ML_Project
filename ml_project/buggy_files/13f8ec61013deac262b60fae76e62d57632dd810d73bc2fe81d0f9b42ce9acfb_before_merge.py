def main(argv: Optional[Sequence[str]] = None, stdin: Optional[TextIOWrapper] = None) -> None:
    arguments = parse_args(argv)
    if arguments.get("show_version"):
        print(ASCII_ART)
        return

    show_config: bool = arguments.pop("show_config", False)

    if "settings_path" in arguments:
        if os.path.isfile(arguments["settings_path"]):
            arguments["settings_file"] = os.path.abspath(arguments["settings_path"])
            arguments["settings_path"] = os.path.dirname(arguments["settings_file"])
        else:
            arguments["settings_path"] = os.path.abspath(arguments["settings_path"])

    if "virtual_env" in arguments:
        venv = arguments["virtual_env"]
        arguments["virtual_env"] = os.path.abspath(venv)
        if not os.path.isdir(arguments["virtual_env"]):
            warn(f"virtual_env dir does not exist: {arguments['virtual_env']}")

    file_names = arguments.pop("files", [])
    if not file_names and not show_config:
        print(QUICK_GUIDE)
        if arguments:
            sys.exit("Error: arguments passed in without any paths or content.")
        else:
            return
    if "settings_path" not in arguments:
        arguments["settings_path"] = (
            os.path.abspath(file_names[0] if file_names else ".") or os.getcwd()
        )
        if not os.path.isdir(arguments["settings_path"]):
            arguments["settings_path"] = os.path.dirname(arguments["settings_path"])

    config_dict = arguments.copy()
    ask_to_apply = config_dict.pop("ask_to_apply", False)
    jobs = config_dict.pop("jobs", ())
    check = config_dict.pop("check", False)
    show_diff = config_dict.pop("show_diff", False)
    write_to_stdout = config_dict.pop("write_to_stdout", False)
    deprecated_flags = config_dict.pop("deprecated_flags", False)
    remapped_deprecated_args = config_dict.pop("remapped_deprecated_args", False)
    wrong_sorted_files = False

    if "src_paths" in config_dict:
        config_dict["src_paths"] = {
            Path(src_path).resolve() for src_path in config_dict.get("src_paths", ())
        }

    config = Config(**config_dict)
    if show_config:
        print(json.dumps(config.__dict__, indent=4, separators=(",", ": "), default=_preconvert))
        return
    elif file_names == ["-"]:
        arguments.setdefault("settings_path", os.getcwd())
        api.sort_stream(
            input_stream=sys.stdin if stdin is None else stdin,
            output_stream=sys.stdout,
            **arguments,
        )
    else:
        skipped: List[str] = []

        if config.filter_files:
            filtered_files = []
            for file_name in file_names:
                if config.is_skipped(Path(file_name)):
                    skipped.append(file_name)
                else:
                    filtered_files.append(file_name)
            file_names = filtered_files

        file_names = iter_source_code(file_names, config, skipped)
        num_skipped = 0
        if config.verbose:
            print(ASCII_ART)

        if jobs:
            import multiprocessing

            executor = multiprocessing.Pool(jobs)
            attempt_iterator = executor.imap(
                functools.partial(
                    sort_imports,
                    config=config,
                    check=check,
                    ask_to_apply=ask_to_apply,
                    write_to_stdout=write_to_stdout,
                ),
                file_names,
            )
        else:
            # https://github.com/python/typeshed/pull/2814
            attempt_iterator = (
                sort_imports(  # type: ignore
                    file_name,
                    config=config,
                    check=check,
                    ask_to_apply=ask_to_apply,
                    show_diff=show_diff,
                    write_to_stdout=write_to_stdout,
                )
                for file_name in file_names
            )

        for sort_attempt in attempt_iterator:
            if not sort_attempt:
                continue  # pragma: no cover - shouldn't happen, satisfies type constraint
            incorrectly_sorted = sort_attempt.incorrectly_sorted
            if arguments.get("check", False) and incorrectly_sorted:
                wrong_sorted_files = True
            if sort_attempt.skipped:
                num_skipped += (
                    1  # pragma: no cover - shouldn't happen, due to skip in iter_source_code
                )

        num_skipped += len(skipped)
        if num_skipped and not arguments.get("quiet", False):
            if config.verbose:
                for was_skipped in skipped:
                    warn(
                        f"{was_skipped} was skipped as it's listed in 'skip' setting"
                        " or matches a glob in 'skip_glob' setting"
                    )
            print(f"Skipped {num_skipped} files")

    if not config.quiet and (remapped_deprecated_args or deprecated_flags):
        if remapped_deprecated_args:
            warn(
                "W0502: The following deprecated single dash CLI flags were used and translated: "
                f"{', '.join(remapped_deprecated_args)}!"
            )
        if deprecated_flags:
            warn(
                "W0501: The following deprecated CLI flags were used and ignored: "
                f"{', '.join(deprecated_flags)}!"
            )
        warn(
            "W0500: Please see the 5.0.0 Upgrade guide: "
            "https://pycqa.github.io/isort/docs/upgrade_guides/5.0.0/"
        )

    if wrong_sorted_files:
        sys.exit(1)