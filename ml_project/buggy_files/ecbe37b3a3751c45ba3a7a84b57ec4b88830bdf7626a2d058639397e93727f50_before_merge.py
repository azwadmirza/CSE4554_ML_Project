def print_run_or_instructions(args: argparse.Namespace, path: Text) -> None:
    from rasa.core import constants
    import questionary

    should_run = (
        questionary.confirm(
            "Do you want to speak to the trained assistant on the command line? 🤖"
        )
        .skip_if(args.no_prompt, default=False)
        .ask()
    )

    if should_run:
        # provide defaults for command line arguments
        attributes = [
            "endpoints",
            "credentials",
            "cors",
            "auth_token",
            "jwt_secret",
            "jwt_method",
            "enable_api",
        ]
        for a in attributes:
            setattr(args, a, None)

        args.port = constants.DEFAULT_SERVER_PORT

        shell(args)
    else:
        if args.no_prompt:
            print (
                "If you want to speak to the assistant, "
                "run 'rasa shell' at any time inside "
                "the project directory."
                "".format(path)
            )
        else:
            print_success(
                "Ok 👍🏼. "
                "If you want to speak to the assistant, "
                "run 'rasa shell' at any time inside "
                "the project directory."
                "".format(path)
            )