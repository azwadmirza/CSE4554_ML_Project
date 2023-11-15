def strip_chunk_signatures(data):
    # For clients that use streaming v4 authentication, the request contains chunk signatures
    # in the HTTP body (see example below) which we need to strip as moto cannot handle them
    #
    # 17;chunk-signature=6e162122ec4962bea0b18bc624025e6ae4e9322bdc632762d909e87793ac5921
    # <payload data ...>
    # 0;chunk-signature=927ab45acd82fc90a3c210ca7314d59fedc77ce0c914d79095f8cc9563cf2c70

    data_new = re.sub(b'(\r\n)?[0-9a-fA-F]+;chunk-signature=[0-9a-f]{64}(\r\n){,2}', b'',
        data, flags=re.MULTILINE | re.DOTALL)
    if data_new != data:
        # trim \r (13) or \n (10)
        for i in range(0, 2):
            if len(data_new) and data_new[0] in (10, 13):
                data_new = data_new[1:]
        for i in range(0, 6):
            if len(data_new) and data_new[-1] in (10, 13):
                data_new = data_new[:-1]
    return data_new