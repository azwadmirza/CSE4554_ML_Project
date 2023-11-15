def encode_atp(atp):
    for k, v in atp.iteritems():
        if isinstance(v, text_type):
            atp[k] = v.encode('utf-8')
    return atp