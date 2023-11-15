def find_multipart_redirect_url(data, headers):
    """ Return object key and redirect URL if they can be found.

        Data is given as multipart form submission bytes, and redirect is found
        in the success_action_redirect field according to Amazon S3
        documentation for Post uploads:
        http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html
    """
    _, params = cgi.parse_header(headers.get('Content-Type', ''))
    key, redirect_url = None, None

    if 'boundary' not in params:
        return key, redirect_url

    boundary = params['boundary'].encode('ascii')
    data_bytes = to_bytes(data)

    for (disposition, part) in _iter_multipart_parts(data_bytes, boundary):
        if disposition.get('name') == 'key':
            _, value = part.split(b'\r\n\r\n', 1)
            key = value.rstrip(b'\r\n--').decode('utf8')

    if key:
        for (disposition, part) in _iter_multipart_parts(data_bytes, boundary):
            if disposition.get('name') == 'success_action_redirect':
                _, value = part.split(b'\r\n\r\n', 1)
                redirect_url = value.rstrip(b'\r\n--').decode('utf8')

    return key, redirect_url