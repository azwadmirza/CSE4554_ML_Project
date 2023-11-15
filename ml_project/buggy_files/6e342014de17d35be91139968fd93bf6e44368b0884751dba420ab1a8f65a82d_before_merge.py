def install():
    _initialize_autocomplete()

    # Where to create the journal?
    path_query = f"Path to your journal file (leave blank for {JOURNAL_FILE_PATH}): "
    journal_path = os.path.abspath(input(path_query).strip() or JOURNAL_FILE_PATH)
    default_config["journals"][DEFAULT_JOURNAL_KEY] = os.path.expanduser(
        os.path.expandvars(journal_path)
    )

    # If the folder doesn't exist, create it
    path = os.path.split(default_config["journals"][DEFAULT_JOURNAL_KEY])[0]
    try:
        os.makedirs(path)
    except OSError:
        pass

    # Encrypt it?
    encrypt = yesno(
        "Do you want to encrypt your journal? You can always change this later",
        default=False,
    )
    if encrypt:
        default_config["encrypt"] = True
        print("Journal will be encrypted.", file=sys.stderr)

    save_config(default_config)
    return default_config