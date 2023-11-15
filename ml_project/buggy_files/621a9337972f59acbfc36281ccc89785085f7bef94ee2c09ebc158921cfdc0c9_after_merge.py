def reject_nuls():
    for key, values in request.values.iterlists():
        if '\0' in key or any('\0' in x for x in values):
            raise BadRequest('NUL byte found in request data')