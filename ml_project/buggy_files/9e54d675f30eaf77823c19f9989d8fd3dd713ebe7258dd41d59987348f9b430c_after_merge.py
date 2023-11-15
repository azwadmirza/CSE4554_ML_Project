def _dict2string(projparams):
    # convert a dict to a proj4 string.
    pjargs = []
    proj_inserted = False
    for key, value in projparams.items():
        # the towgs84 as list
        if isinstance(value, (list, tuple)):
            value = ",".join([str(val) for val in value])
        # issue 183 (+ no_rot)
        if value is None or value is True:
            pjargs.append("+{key}".format(key=key))
        elif value is False:
            pass
        # make sure string starts with proj or init
        elif not proj_inserted and key in ("init", "proj"):
            pjargs.insert(0, "+{key}={value}".format(key=key, value=value))
            proj_inserted = True
        else:
            pjargs.append("+{key}={value}".format(key=key, value=value))
    return " ".join(pjargs)