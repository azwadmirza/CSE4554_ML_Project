def getFilterSettingsFromPost(r):
    filters = dict(request.form)
    filters = {x: filters[x][0] for x in filters.keys()}
    errors  = False
    # retrieving data
    try:
      cve = filter_logic(filters, pageLength, r)
    except:
      cve = dbLayer.getCVEs(limit=pageLength, skip=r)
      errors = True
    return(filters,cve,errors)