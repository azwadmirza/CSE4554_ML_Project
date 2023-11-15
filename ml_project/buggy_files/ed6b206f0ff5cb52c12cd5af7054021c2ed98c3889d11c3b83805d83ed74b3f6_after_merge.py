def decode_methods_request(offset, data):
    """
    Try to decodes a METHOD request
    @param int offset: the offset to start in the data
    @param str data: the serialised data to decode from
    @return: Tuple (offset, None) on failure, else (new_offset, MethodRequest)
    @rtype: (int, None|MethodRequest)
    """
    # Check if we have enough bytes
    if len(data) - offset < 2:
        return offset, None

    (version, number_of_methods) = struct.unpack_from("!BB", data, offset)

    offset += 2

    # Check whether there are enough bytes for the number of methods
    if len(data) - offset < number_of_methods:
        return offset, None

    methods = set([])
    for i in range(number_of_methods):
        method, = struct.unpack_from("!B", data, offset)
        methods.add(method)
        offset += 1

    return offset, MethodRequest(version, methods)