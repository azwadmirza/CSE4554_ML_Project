def store_credentials(credentials, overwrite=False, filename=None):
    """
    Store the credentials for a single account in the configuration file.

    Args:
        credentials (Credentials): credentials instance.
        overwrite (bool): overwrite existing credentials.
        filename (str): full path to the qiskitrc file. If `None`, the default
            location is used (`HOME/.qiskit/qiskitrc`).

    Raises:
        QISKitError: If credentials already exists and overwrite=False; or if
            the account_name could not be assigned.
    """
    # Read the current providers stored in the configuration file.
    filename = filename or DEFAULT_QISKITRC_FILE
    stored_credentials = read_credentials_from_qiskitrc(filename)

    if credentials.unique_id() in stored_credentials and not overwrite:
        raise QISKitError('Credentials already present and overwrite=False')

    # Append and write the credentials to file.
    stored_credentials[credentials.unique_id()] = credentials
    write_qiskit_rc(stored_credentials, filename)