def getURL(url, post_data=None, params=None, headers=None,  # pylint:disable=too-many-arguments, too-many-return-statements, too-many-branches, too-many-locals
           timeout=30, session=None, **kwargs):
    """
    Returns data retrieved from the url provider.
    """
    response_type = kwargs.pop(u'returns', u'response')
    stream = kwargs.pop(u'stream', False)
    hooks, cookies, verify, proxies = request_defaults(kwargs)
    method = u'POST' if post_data else u'GET'

    try:
        resp = session.request(method, url, data=post_data, params=params, timeout=timeout, allow_redirects=True,
                               hooks=hooks, stream=stream, headers=headers, cookies=cookies, proxies=proxies,
                               verify=verify)

        if not resp.ok:
            logger.log(u'Requested url {url} returned status code {status}: {desc}'.format
                       (url=url, status=resp.status_code, desc=http_code_description(resp.status_code)), logger.DEBUG)

    except requests.exceptions.RequestException as e:
        logger.log(u'Error requesting url {resp.url}. Error: {msg}'.format(resp=resp, msg=ex(e)), logger.DEBUG)
    except Exception as e:
        if u'ECONNRESET' in e or (hasattr(e, u'errno') and e.errno == errno.ECONNRESET):
            logger.log(u'Connection reset by peer accessing url {resp.url}. Error: {msg}'.format(resp=resp, msg=ex(e)), logger.WARNING)
        else:
            logger.log(u'Unknown exception in url {resp.url}. Error: {msg}'.format(resp=resp, msg=ex(e)), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)

    if not response_type or response_type == u'response':
        return resp
    else:
        warnings.warn(u'Returning {0} instead of {1} will be deprecated in the near future!'.format
                      (response_type, 'response'), PendingDeprecationWarning)
        if response_type == u'json':
            try:
                return resp.json()
            except ValueError:
                return {}
        else:
            return getattr(resp, response_type, resp)