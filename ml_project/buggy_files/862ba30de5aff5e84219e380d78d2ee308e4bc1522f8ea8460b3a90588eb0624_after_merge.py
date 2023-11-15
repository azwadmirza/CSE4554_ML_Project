def create_parser():
    p = argparse.ArgumentParser()
    sub_parsers = p.add_subparsers()

    main_create.configure_parser(sub_parsers)
    main_export.configure_parser(sub_parsers)
    main_list.configure_parser(sub_parsers)
    main_remove.configure_parser(sub_parsers)
    return p