def apidbInfo():
    return (json.dumps(dbLayer.getDBStats()))