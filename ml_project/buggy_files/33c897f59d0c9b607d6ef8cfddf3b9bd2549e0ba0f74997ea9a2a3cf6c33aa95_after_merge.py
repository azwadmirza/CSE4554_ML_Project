def apidbInfo():
    return json.dumps(dbLayer.getDBStats(), default=json_util.default)