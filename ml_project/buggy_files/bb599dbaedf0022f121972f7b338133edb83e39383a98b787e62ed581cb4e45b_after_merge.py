def run(args: argparse.Namespace) -> None:
    import questionary

    print_success("Welcome to Rasa! 🤖\n")
    if args.no_prompt:
        print(
            "To get started quickly, an "
            "initial project will be created.\n"
            "If you need some help, check out "
            "the documentation at {}.\n".format(DOCS_BASE_URL)
        )
    else:
        print(
            "To get started quickly, an "
            "initial project will be created.\n"
            "If you need some help, check out "
            "the documentation at {}.\n"
            "Now let's start! 👇🏽\n".format(DOCS_BASE_URL)
        )

    path = (
        questionary.text(
            "Please enter a path where the project will be "
            "created [default: current directory]",
            default=".",
        )
        .skip_if(args.no_prompt, default=".")
        .ask()
    )

    if path and not os.path.isdir(path):
        _ask_create_path(path)

    if path is None or not os.path.isdir(path):
        print_cancel()

    if not args.no_prompt and len(os.listdir(path)) > 0:
        _ask_overwrite(path)

    init_project(args, path)