def pauseMonitor(module, params):

    params['monitorStatus'] = 0
    data = urlencode(params)
    full_uri = API_BASE + API_ACTIONS['editMonitor'] + data
    req, info = fetch_url(module, full_uri)
    result = req.read()
    jsonresult = json.loads(result)
    req.close()
    return jsonresult['stat']