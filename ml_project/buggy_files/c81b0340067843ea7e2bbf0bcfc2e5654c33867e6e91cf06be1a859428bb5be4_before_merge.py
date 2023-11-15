def salt_api():
    '''
    The main function for salt-api
    '''
    import salt.cli.api
    sapi = salt.cli.api.SaltAPI()  # pylint: disable=E1120
    sapi.run()