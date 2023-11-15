def format_flow_data(key, scope, flow):
    data = b""
    if scope in ("q", "b"):
        request = flow.request.copy()
        request.decode(strict=False)
        if request.content is None:
            return None, "Request content is missing"
        if key == "h":
            data += netlib.http.http1.assemble_request(request)
        elif key == "c":
            data += request.get_content(strict=False)
        else:
            raise ValueError("Unknown key: {}".format(key))
    if scope == "b" and flow.request.raw_content and flow.response:
        # Add padding between request and response
        data += b"\r\n" * 2
    if scope in ("s", "b") and flow.response:
        response = flow.response.copy()
        response.decode(strict=False)
        if response.content is None:
            return None, "Response content is missing"
        if key == "h":
            data += netlib.http.http1.assemble_response(response)
        elif key == "c":
            data += response.get_content(strict=False)
        else:
            raise ValueError("Unknown key: {}".format(key))
    return data, False