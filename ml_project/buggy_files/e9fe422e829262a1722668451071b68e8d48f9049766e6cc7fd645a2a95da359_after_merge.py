def apiCVE(cveid):
    cvesp = cves.last(rankinglookup=True, namelookup=True, vfeedlookup=True, capeclookup=True)
    cve = cvesp.getcve(cveid=cveid)
    if cve is None:
        cve = {}
    return jsonify(cve)