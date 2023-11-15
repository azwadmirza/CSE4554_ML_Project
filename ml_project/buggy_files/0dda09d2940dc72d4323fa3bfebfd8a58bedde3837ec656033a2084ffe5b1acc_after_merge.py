def is_internet_available():
    try:
        proxies, verify = upstream_proxy('https')
    except Exception:
        logger.exception('Setting upstream proxy')
    try:
        requests.get(settings.GOOGLE,
                     timeout=5,
                     proxies=proxies,
                     verify=verify)
        return True
    except Exception:
        try:
            requests.get(settings.BAIDU,
                         timeout=5,
                         proxies=proxies,
                         verify=verify)
            return True
        except Exception:
            return False