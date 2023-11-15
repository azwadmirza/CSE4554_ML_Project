def _get_gcp_credentials(module, require_valid_json=True, check_libcloud=False):
    """
    Obtain GCP credentials by trying various methods.

    There are 3 ways to specify GCP credentials:
    1. Specify via Ansible module parameters (recommended).
    2. Specify via environment variables.  Two sets of env vars are available:
       a) GOOGLE_CLOUD_PROJECT, GOOGLE_CREDENTIALS_APPLICATION (preferred)
       b) GCE_PROJECT, GCE_CREDENTIAL_FILE_PATH, GCE_EMAIL (legacy, not recommended; req'd if
          using p12 key)
    3. Specify via libcloud secrets.py file (deprecated).

    There are 3 helper functions to assist in the above.

    Regardless of method, the user also has the option of specifying a JSON
    file or a p12 file as the credentials file.  JSON is strongly recommended and
    p12 will be removed in the future.

    Additionally, flags may be set to require valid json and check the libcloud
    version.

    AnsibleModule.fail_json is called only if the project_id cannot be found.

    :param module: initialized Ansible module object
    :type module: `class AnsibleModule`

    :param require_valid_json: If true, require credentials to be valid JSON.  Default is True.
    :type require_valid_json: ``bool``

    :params check_libcloud: If true, check the libcloud version available to see if
                            JSON creds are supported.
    :type check_libcloud: ``bool``

    :return:  {'service_account_email': service_account_email,
               'credentials_file': credentials_file,
                'project_id': project_id}
    :rtype: ``dict``
    """
    (service_account_email,
     credentials_file,
     project_id) = _get_gcp_ansible_credentials(module)

    # If any of the values are not given as parameters, check the appropriate
    # environment variables.
    (service_account_email,
     credentials_file,
     project_id) = _get_gcp_environment_credentials(service_account_email,
                                                    credentials_file, project_id)

    # If we still don't have one or more of our credentials, attempt to
    # get the remaining values from the libcloud secrets file.
    (service_account_email,
     credentials_file,
     project_id) = _get_gcp_libcloud_credentials(service_account_email,
                                                 credentials_file, project_id)

    if credentials_file is None or project_id is None or service_account_email is None:
        if check_libcloud is True:
            if project_id is None:
                # TODO(supertom): this message is legacy and integration tests
                # depend on it.
                module.fail_json(msg='Missing GCE connection parameters in libcloud '
                                 'secrets file.')
        else:
            if project_id is None:
                module.fail_json(msg=('GCP connection error: unable to determine project (%s) or '
                                      'credentials file (%s)' % (project_id, credentials_file)))
        # Set these fields to empty strings if they are None
        # consumers of this will make the distinction between an empty string
        # and None.
        if credentials_file is None:
            credentials_file = ''
        if service_account_email is None:
            service_account_email = ''

    # ensure the credentials file is found and is in the proper format.
    if credentials_file:
        _validate_credentials_file(module, credentials_file,
                                   require_valid_json=require_valid_json,
                                   check_libcloud=check_libcloud)

    return {'service_account_email': service_account_email,
            'credentials_file': credentials_file,
            'project_id': project_id}