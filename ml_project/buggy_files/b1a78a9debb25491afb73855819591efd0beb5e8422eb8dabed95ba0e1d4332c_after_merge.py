def _configure_iam_role(config):
    """Setup a gcp service account with IAM roles.

    Creates a gcp service acconut and binds IAM roles which allow it to control
    control storage/compute services. Specifically, the head node needs to have
    an IAM role that allows it to create further gce instances and store items
    in google cloud storage.

    TODO: Allow the name/id of the service account to be configured
    """
    email = SERVICE_ACCOUNT_EMAIL_TEMPLATE.format(
        account_id=DEFAULT_SERVICE_ACCOUNT_ID,
        project_id=config["provider"]["project_id"])
    service_account = _get_service_account(email, config)

    if service_account is None:
        logger.info("Creating new service account {}".format(
            DEFAULT_SERVICE_ACCOUNT_ID))

        service_account = _create_service_account(
            DEFAULT_SERVICE_ACCOUNT_ID, DEFAULT_SERVICE_ACCOUNT_CONFIG, config)

    assert service_account is not None, "Failed to create service account"

    _add_iam_policy_binding(service_account, DEFAULT_SERVICE_ACCOUNT_ROLES)

    config["head_node"]["serviceAccounts"] = [{
        "email": service_account["email"],
        # NOTE: The amount of access is determined by the scope + IAM
        # role of the service account. Even if the cloud-platform scope
        # gives (scope) access to the whole cloud-platform, the service
        # account is limited by the IAM rights specified below.
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
    }]

    return config