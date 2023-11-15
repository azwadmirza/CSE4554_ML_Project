def expand_multipart_filename(data, headers):
    """ Replace instance of '${filename}' in key with given file name.

        Data is given as multipart form submission bytes, and file name is
        replace according to Amazon S3 documentation for Post uploads:
        http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html
    """
    _, params = cgi.parse_header(headers.get('Content-Type', ''))

    if 'boundary' not in params:
        return data

    boundary = params['boundary'].encode('ascii')
    data_bytes = to_bytes(data)

    filename = None

    for (disposition, _) in _iter_multipart_parts(data_bytes, boundary):
        if disposition.get('name') == 'file' and 'filename' in disposition:
            filename = disposition['filename']
            break

    if filename is None:
        # Found nothing, return unaltered
        return data

    for (disposition, part) in _iter_multipart_parts(data_bytes, boundary):
        if disposition.get('name') == 'key' and b'${filename}' in part:
            search = boundary + part
            replace = boundary + part.replace(b'${filename}', filename.encode('utf8'))

            if search in data_bytes:
                return data_bytes.replace(search, replace)

    return data