def stop_httptools(url):
    """Kill httptools."""
    # Invoke HTTPtools UI Kill Request
    try:
        requests.get(f'{url}/kill', timeout=5)
        logger.info('Killing httptools UI')
    except Exception:
        pass

    # Invoke HTTPtools Proxy Kill Request
    try:
        http_proxy = url.replace('https://', 'http://')
        headers = {'httptools': 'kill'}
        url = 'http://127.0.0.1'
        requests.get(url, headers=headers, proxies={
                     'http': http_proxy})
        logger.info('Killing httptools Proxy')
    except Exception:
        pass