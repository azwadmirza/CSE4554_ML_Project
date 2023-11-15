def isInternetAvailable():
    try:
        proxies, verify = upstream_proxy('https')
    except:
        PrintException("Setting upstream proxy")
    try:
        requests.get('https://www.google.com', timeout=5,
                     proxies=proxies, verify=verify)
        return True
    except requests.exceptions.HTTPError as err:
        try:
            requests.get('https://www.baidu.com/', timeout=5,
                         proxies=proxies, verify=verify)
            return True
        except requests.exceptions.HTTPError as err1:
            return False
    return False