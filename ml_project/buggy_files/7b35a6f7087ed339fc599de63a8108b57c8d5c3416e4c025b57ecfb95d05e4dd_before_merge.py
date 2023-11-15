def login(url=None, username=None, password=None, email=None):
    '''
    Wrapper to the ``docker.py`` login method (does not do much yet)

    url
        registry url to authenticate to

    username
        username to authenticate

    password
        password to authenticate

    email
        email to authenticate

    CLI Example:

    .. code-block:: bash

        salt '*' docker.login <url> <username> <password> <email>
    '''
    client = _get_client()
    return client.login(url, username, password, email)