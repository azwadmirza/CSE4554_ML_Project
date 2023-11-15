def stop_httptools(port):
    """Kill httptools."""
    # Invoke HTTPtools UI Kill Request
    try:
        requests.get('http://127.0.0.1:' + str(port) + '/kill', timeout=5)
        logger.info('Killing httptools UI')
    except Exception:
        pass

    # Inkoke HTTPtools Proxy Kill Request
    try:
        http_proxy = 'http://127.0.0.1:' + str(port)
        headers = {'httptools': 'kill'}
        url = 'http://127.0.0.1'
        requests.get(url, headers=headers, proxies={
                     'http': http_proxy})
        logger.info('Killing httptools Proxy')
    except Exception:
        pass