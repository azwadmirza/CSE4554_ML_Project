def _get_gcp_libcloud_credentials(module, service_account_email=None, credentials_file=None, project_id=None):
    """
    Helper to look for libcloud secrets.py file.

    Note: This has an 'additive' effect right now, filling in
    vars not specified elsewhere, in order to keep legacy functionality.
    This method of specifying credentials will be deprecated, otherwise
    we'd look to make it more restrictive with an all-vars-or-nothing approach.

    :param service_account: GCP service account email used to make requests
    :type service_account: ``str`` or None

    :param credentials_file: Path on disk to credentials file
    :type credentials_file: ``str`` or None

    :param project_id: GCP project ID.
    :type project_id: ``str`` or None

    :return: tuple of (service_account, credentials_file, project_id)
    :rtype: ``tuple`` of ``str``
    """
    if service_account_email is None or credentials_file is None:
        try:
            import secrets
            module.deprecate(msg=("secrets file found at '%s'.  This method of specifying "
                                  "credentials is deprecated.  Please use env vars or "
                                  "Ansible YAML files instead" % (secrets.__file__)), version=2.5)
        except ImportError:
            secrets = None
        if hasattr(secrets, 'GCE_PARAMS'):
            if not service_account_email:
                service_account_email = secrets.GCE_PARAMS[0]
            if not credentials_file:
                credentials_file = secrets.GCE_PARAMS[1]
        keyword_params = getattr(secrets, 'GCE_KEYWORD_PARAMS', {})
        if not project_id:
            project_id = keyword_params.get('project', None)
    return (service_account_email, credentials_file, project_id)