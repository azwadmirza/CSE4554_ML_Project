def apibrowse(vendor=None):
    if vendor is not None:
        vendor = urllib.parse.quote_plus(vendor).lower()
    browseList = getBrowseList(vendor)
    if isinstance(browseList, dict):
        return jsonify(browseList)
    else:
        return jsonify({})