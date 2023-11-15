def get_url(url, post_data=None, params=None, headers=None, timeout=30, session=None, **kwargs):
    """Return data retrieved from the url provider."""
    response_type = kwargs.pop(u'returns', u'response')
    stream = kwargs.pop(u'stream', False)
    hooks, cookies, verify, proxies = request_defaults(kwargs)
    method = u'POST' if post_data else u'GET'

    try:
        req = requests.Request(method, url, data=post_data, params=params, hooks=hooks,
                               headers=headers, cookies=cookies)
        prepped = session.prepare_request(req)
        resp = session.send(prepped, stream=stream, verify=verify, proxies=proxies, timeout=timeout,
                            allow_redirects=True)

        if not resp.ok:
            # Try to bypass CloudFlare's anti-bot protection
            if resp.status_code == 503 and resp.headers.get('server') == u'cloudflare-nginx':
                cf_prepped = prepare_cf_req(session, req)
                if cf_prepped:
                    cf_resp = session.send(cf_prepped, stream=stream, verify=verify, proxies=proxies,
                                           timeout=timeout, allow_redirects=True)
                    if cf_resp.ok:
                        return cf_resp

            logger.debug(u'Requested url {url} returned status code {status}: {desc}'.format
                         (url=resp.url, status=resp.status_code, desc=http_code_description(resp.status_code)))

            if response_type and response_type != u'response':
                return None

    except requests.exceptions.RequestException as e:
        logger.debug(u'Error requesting url {url}. Error: {err_msg}', url=url, err_msg=e)
        return None
    except Exception as e:
        if u'ECONNRESET' in e or (hasattr(e, u'errno') and e.errno == errno.ECONNRESET):
            logger.warning(u'Connection reset by peer accessing url {url}. Error: {err_msg}'.format(url=url, err_msg=e))
        else:
            logger.info(u'Unknown exception in url {url}. Error: {err_msg}', url=url, err_msg=e)
            logger.debug(traceback.format_exc())
        return None

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
            return getattr(resp, response_type, None)