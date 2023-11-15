def list_journal_directory(context, journal="default"):
    with open(context.config_path) as config_file:
        configuration = yaml.load(config_file, Loader=yaml.FullLoader)
    journal_path = configuration["journals"][journal]
    for root, dirnames, f in os.walk(journal_path):
        for file in f:
            print(os.path.join(root, file))