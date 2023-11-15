def apidbInfo():
    return (json.dumps(db.getDBStats()))