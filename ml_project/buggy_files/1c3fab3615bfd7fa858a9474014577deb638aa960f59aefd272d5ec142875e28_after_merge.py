def build_docs(context, site_name=None, view=True):
    """Build documentation in a context"""
    logger.debug("Starting cli.datasource.build_docs")

    cli_message("Building Data Docs...")

    if site_name is not None:
        site_names = [site_name]
    else:
        site_names = None

    index_page_locator_infos = context.build_data_docs(site_names=site_names)

    msg = "The following Data Docs sites were built:\n"
    for site_name, index_page_locator_info in index_page_locator_infos.items():
        if os.path.isfile(index_page_locator_info):
            msg += " - <cyan>{}:</cyan> ".format(site_name)
            msg += "file://{}\n".format(index_page_locator_info)
        else:
            msg += " - <cyan>{}:</cyan> ".format(site_name)
            msg += "{}\n".format(index_page_locator_info)

    msg = msg.rstrip("\n")
    cli_message(msg)

    if view:
        context.open_data_docs(site_name=site_name)