def checkID(module, params):

    data = urlencode(params)
    full_uri = API_BASE + API_ACTIONS['status'] + data
    req, info = fetch_url(module, full_uri)
    result = to_text(req.read())
    jsonresult = json.loads(result)
    req.close()
    return jsonresult