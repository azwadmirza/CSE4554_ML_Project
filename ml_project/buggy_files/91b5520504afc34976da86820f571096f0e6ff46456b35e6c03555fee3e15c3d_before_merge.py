def init(opts):
    '''
    Required.
    Can be used to initialize the server connection.
    '''
    try:
        DETAILS['server'] = SSHConnection(host=__opts__['proxy']['host'],
                                          username=__opts__['proxy']['username'],
                                          password=__opts__['proxy']['password'])
        out, err = DETAILS['server'].sendline('help')
        log.debug(out)

    except TerminalException as e:
        log.error(e)
        return False