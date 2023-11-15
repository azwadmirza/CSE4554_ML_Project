def main(args):
    """
    Store the defect results in the specified input list as bug reports in the
    database.
    """

    if not host_check.check_zlib():
        raise Exception("zlib is not available on the system!")

    # To ensure the help message prints the default folder properly,
    # the 'default' for 'args.input' is a string, not a list.
    # But we need lists for the foreach here to work.
    if isinstance(args.input, str):
        args.input = [args.input]

    if 'name' not in args:
        LOG.debug("Generating name for analysis...")
        generated = __get_run_name(args.input)
        if generated:
            setattr(args, 'name', generated)
        else:
            LOG.error("No suitable name was found in the inputs for the "
                      "analysis run. Please specify one by passing argument "
                      "--name run_name in the invocation.")
            sys.exit(2)  # argparse returns error code 2 for bad invocations.

    LOG.info("Storing analysis results for run '" + args.name + "'")

    if 'force' in args:
        LOG.info("argument --force was specified: the run with name '" +
                 args.name + "' will be deleted.")

    _, host, port, product_name = split_product_url(args.product_url)

    # Before any transmission happens, check if we have the PRODUCT_STORE
    # permission to prevent a possibly long ZIP operation only to get an
    # error later on.
    product_client = libclient.setup_product_client(host, port, product_name)
    product_id = product_client.getCurrentProduct().id

    auth_client, _ = libclient.setup_auth_client(host, port)
    has_perm = libclient.check_permission(
        auth_client, Permission.PRODUCT_STORE, {'productID': product_id})
    if not has_perm:
        LOG.error("You are not authorised to store analysis results in "
                  "product '{0}'".format(product_name))
        sys.exit(1)

    # Setup connection to the remote server.
    client = libclient.setup_client(args.product_url)

    LOG.debug("Initializing client connecting to {0}:{1}/{2} done."
              .format(host, port, product_name))

    _, zip_file = tempfile.mkstemp('.zip')
    LOG.debug("Will write mass store ZIP to '{0}'...".format(zip_file))

    try:
        assemble_zip(args.input, zip_file, client)
        with open(zip_file, 'rb') as zf:
            b64zip = base64.b64encode(zf.read())

        context = generic_package_context.get_context()

        client.massStoreRun(args.name,
                            context.version,
                            b64zip,
                            'force' in args)

        LOG.info("Storage finished successfully.")
    except Exception as ex:
        LOG.info("Storage failed: " + str(ex))
        sys.exit(1)
    finally:
        os.remove(zip_file)