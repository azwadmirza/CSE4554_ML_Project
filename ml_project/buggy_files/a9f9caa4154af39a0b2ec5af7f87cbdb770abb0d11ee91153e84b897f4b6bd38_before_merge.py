def create_parser():
    p = argparse.ArgumentParser()
    sub_parsers = p.add_subparsers()

    main_attach.configure_parser(sub_parsers)
    main_create.configure_parser(sub_parsers)
    main_export.configure_parser(sub_parsers)
    main_list.configure_parser(sub_parsers)
    main_remove.configure_parser(sub_parsers)
    main_upload.configure_parser(sub_parsers)
    main_update.configure_parser(sub_parsers)

    show_help_on_empty_command()
    return p