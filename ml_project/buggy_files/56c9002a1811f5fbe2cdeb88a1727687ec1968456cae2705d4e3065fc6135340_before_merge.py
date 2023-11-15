def run_hydra(args_parser, task_function, config_path, strict):
    from .hydra import Hydra

    calling_file, calling_module = detect_calling_file_or_module(3)
    config_dir, config_file = split_config_path(config_path)
    strict = _strict_mode_strategy(strict, config_file)
    task_name = detect_task_name(calling_file, calling_module)
    search_path = create_automatic_config_search_path(
        calling_file, calling_module, config_dir
    )

    hydra = Hydra.create_main_hydra2(
        task_name=task_name, config_search_path=search_path, strict=strict
    )

    args = args_parser.parse_args()
    if args.help:
        hydra.app_help(config_file=config_file, args_parser=args_parser, args=args)
        sys.exit(0)
    if args.hydra_help:
        hydra.hydra_help(config_file=config_file, args_parser=args_parser, args=args)
        sys.exit(0)

    has_show_cfg = args.cfg is not None
    num_commands = args.run + has_show_cfg + args.multirun + args.shell_completion
    if num_commands > 1:
        raise ValueError(
            "Only one of --run, --multirun,  -cfg and --shell_completion can be specified"
        )
    if num_commands == 0:
        args.run = True
    if args.run:
        hydra.run(
            config_file=config_file,
            task_function=task_function,
            overrides=args.overrides,
        )
    elif args.multirun:
        hydra.multirun(
            config_file=config_file,
            task_function=task_function,
            overrides=args.overrides,
        )
    elif args.cfg:
        hydra.show_cfg(overrides=args.overrides, cfg_type=args.cfg)
    elif args.shell_completion:
        hydra.shell_completion(config_file=config_file, overrides=args.overrides)
    else:
        print("Command not specified")
        sys.exit(1)