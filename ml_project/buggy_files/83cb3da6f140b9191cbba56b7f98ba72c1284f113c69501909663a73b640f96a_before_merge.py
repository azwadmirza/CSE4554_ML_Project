def close_client():
    '''End docker interactions by closing the client. This is meant to be
    used after analysis is done'''
    try:
        client.close()
    except requests.exceptions.ConnectionError:
        # it should either already be closed or docker is not setup
        # either way, the socket is closed
        pass