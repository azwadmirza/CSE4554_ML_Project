def apisearch(vendor=None, product=None):
    if vendor is None or product is None:
        return jsonify({})
    search = vendor + ":" + product
    return json.dumps(db.cvesForCPE(search), default=json_util.default)