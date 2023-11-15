def _validate_credentials_file(module, credentials_file, require_valid_json=True, check_libcloud=False):
    """
    Check for valid credentials file.

    Optionally check for JSON format and if libcloud supports JSON.

    :param module: initialized Ansible module object
    :type module: `class AnsibleModule`

    :param credentials_file: path to file on disk
    :type credentials_file: ``str``.  Complete path to file on disk.

    :param require_valid_json: If true, require credentials to be valid JSON.  Default is True.
    :type require_valid_json: ``bool``

    :params check_libcloud: If true, check the libcloud version available to see if
                            JSON creds are supported.
    :type check_libcloud: ``bool``

    :returns: True
    :rtype: ``bool``
    """
    try:
        # Try to read credentials as JSON
        with open(credentials_file) as credentials:
            json.loads(credentials.read())
            # If the credentials are proper JSON and we do not have the minimum
            # required libcloud version, bail out and return a descriptive
            # error
            if check_libcloud and LooseVersion(libcloud.__version__) < '0.17.0':
                module.fail_json(msg='Using JSON credentials but libcloud minimum version not met. '
                                     'Upgrade to libcloud>=0.17.0.')
            return True
    except IOError as e:
        module.fail_json(msg='GCP Credentials File %s not found.' %
                         credentials_file, changed=False)
        return False
    except ValueError as e:
        if require_valid_json:
            module.fail_json(
                msg='GCP Credentials File %s invalid.  Must be valid JSON.' % credentials_file, changed=False)
        else:
            display.deprecated(msg=("Non-JSON credentials file provided. This format is deprecated. "
                                    " Please generate a new JSON key from the Google Cloud console"),
                               version=2.5)
            return True