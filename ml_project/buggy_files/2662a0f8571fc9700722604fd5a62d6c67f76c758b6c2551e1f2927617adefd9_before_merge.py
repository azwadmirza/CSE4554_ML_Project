def setup_api():
    session = Session()
    session.mount(API_HOST, host_header_ssl.HostHeaderSSLAdapter())
    session.headers.update({'Host': PRODUCTION_DOMAIN})
    api_config = {
        'base_url': '%s/api/v1/' % API_HOST,
        'session': session,
    }
    if USER and PASS:
        log.debug('Using slumber with user %s, pointed at %s', USER, API_HOST)
        session.auth = (USER, PASS)
    else:
        log.warning('SLUMBER_USERNAME/PASSWORD settings are not set')
    return API(**api_config)