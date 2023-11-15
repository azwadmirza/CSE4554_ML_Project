def setup_api():
    session = requests.Session()
    session.mount(
        API_HOST,
        host_header_ssl.HostHeaderSSLAdapter(
            max_retries=3,
        ),
    )
    session.headers.update({'Host': PRODUCTION_DOMAIN})
    api_config = {
        'base_url': '%s/api/v2/' % API_HOST,
        'serializer': serialize.Serializer(
            default='json-drf',
            serializers=[
                serialize.JsonSerializer(),
                DrfJsonSerializer(),
            ],
        ),
        'session': session,
    }
    if USER and PASS:
        log.debug(
            'Using slumber v2 with user %s, pointed at %s',
            USER,
            API_HOST,
        )
        session.auth = (USER, PASS)
    else:
        log.warning('SLUMBER_USERNAME/PASSWORD settings are not set')
    return API(**api_config)