def apiCVEFor(cpe):
    cpe=urllib.parse.unquote_plus(cpe)
    cpe=toStringFormattedCPE(cpe)
    r = []
    cvesp = cves.last(rankinglookup=False, namelookup=False, vfeedlookup=True, capeclookup=False)
    for x in db.cvesForCPE(cpe):
        r.append(cvesp.getcve(x['id']))
    return json.dumps(r)