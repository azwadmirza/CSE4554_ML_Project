def apidbInfo():
    return json.dumps(db.getDBStats(), default=json_util.default)