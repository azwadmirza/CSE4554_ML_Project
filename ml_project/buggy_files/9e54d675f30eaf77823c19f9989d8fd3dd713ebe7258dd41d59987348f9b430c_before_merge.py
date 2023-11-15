def _dict2string(projparams):
    # convert a dict to a proj4 string.
    pjargs = []
    for key, value in projparams.items():
        # the towgs84 as list
        if isinstance(value, (list, tuple)):
            value = ",".join([str(val) for val in value])
        # issue 183 (+ no_rot)
        if value is None or value is True:
            pjargs.append("+" + key + " ")
        elif value is False:
            pass
        else:
            pjargs.append("+" + key + "=" + str(value) + " ")
    return "".join(pjargs)