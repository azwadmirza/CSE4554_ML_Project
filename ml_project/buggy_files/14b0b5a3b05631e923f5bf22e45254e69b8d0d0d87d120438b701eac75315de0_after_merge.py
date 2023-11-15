def apiCVEFor(cpe):
    cpe=urllib.parse.unquote_plus(cpe)
    cpe=toStringFormattedCPE(cpe)
    if not cpe: cpe='None'
    r = []
    cvesp = cves.last(rankinglookup=False, namelookup=False, vfeedlookup=True, capeclookup=False)
    for x in dbLayer.cvesForCPE(cpe):
        r.append(cvesp.getcve(x['id']))
    return json.dumps(r, default=json_util.default)