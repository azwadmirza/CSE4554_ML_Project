def verify_cli_version():
    os.environ["OUTDATED_IGNORE"] = 1
    try:

        version = pkg_resources.get_distribution(hub.__name__).version
        is_outdated, latest_version = check_outdated(hub.__name__, version)
        if is_outdated:
            print(
                "\033[93m"
                + "Hub is out of date. Please upgrade the package by running `pip3 install --upgrade snark`"
                + "\033[0m"
            )
    except Exception as e:
        logger.error(str(e))