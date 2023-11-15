def get_data_dir():
    default_data_dir = Path(appdir.user_data_dir)

    print(
        "Hello! Before we begin the full configuration process we need to"
        " gather some initial information about where you'd like us"
        " to store your bot's data. We've attempted to figure out a"
        " sane default data location which is printed below. If you don't"
        " want to change this default please press [ENTER], otherwise"
        " input your desired data location."
    )
    print()
    print("Default: {}".format(default_data_dir))

    new_path = input("> ")

    if new_path != "":
        new_path = Path(new_path)
        default_data_dir = new_path

    if not default_data_dir.exists():
        try:
            default_data_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            print(
                "We were unable to create your chosen directory."
                " You may need to restart this process with admin"
                " privileges."
            )
            sys.exit(1)

    print("You have chosen {} to be your data directory.".format(default_data_dir))
    if not confirm("Please confirm (y/n):"):
        print("Please start the process over.")
        sys.exit(0)
    return default_data_dir