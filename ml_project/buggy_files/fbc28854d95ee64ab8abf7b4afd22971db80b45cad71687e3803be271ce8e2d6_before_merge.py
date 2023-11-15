def __virtual__():
    """
    Set up the libcloud functions and check for GCE configurations.
    """
    if get_configured_provider() is False:
        return False

    if get_dependencies() is False:
        return False

    for provider, details in __opts__["providers"].items():
        if "gce" not in details:
            continue

        parameters = details["gce"]
        pathname = os.path.expanduser(parameters["service_account_private_key"])
        # empty pathname will tell libcloud to use instance credentials
        if (
            pathname
            and salt.utils.cloud.check_key_path_and_mode(provider, pathname) is False
        ):
            return False

    return __virtualname__