def publish_module(environ, start_response,
                   _publish=publish,  # only for testing
                   _response=None,
                   _response_factory=WSGIResponse,
                   _request=None,
                   _request_factory=WSGIRequest,
                   _module_name='Zope2'):
    module_info = get_module_info(_module_name)
    result = ()

    path_info = environ.get('PATH_INFO')
    if path_info and PY3:
        # BIG Comment, see discussion at
        # https://github.com/zopefoundation/Zope/issues/575
        #
        # The WSGI server automatically treats headers, including the
        # PATH_INFO, as latin-1 encoded bytestrings, according to PEP-3333. As
        # this causes headache I try to show the steps a URI takes in WebOb,
        # which is similar in other wsgi server implementations.
        # UTF-8 URL-encoded object-id 'täst':
        #   http://localhost/t%C3%A4st
        # unquote('/t%C3%A4st'.decode('ascii')) results in utf-8 encoded bytes
        #   b'/t\xc3\xa4st'
        # b'/t\xc3\xa4st'.decode('latin-1') latin-1 decoding due to PEP-3333
        #   '/tÃ¤st'
        # We now have a latin-1 decoded text, which was actually utf-8 encoded.
        # To reverse this we have to encode with latin-1 first.
        path_info = path_info.encode('latin-1')

        # So we can now decode with the right (utf-8) encoding to get text.
        # This encode/decode two-step with different encodings works because
        # of the way PEP-3333 restricts the type of string allowable for
        # request and response metadata. The allowed characters match up in
        # both latin-1 and utf-8.
        path_info = path_info.decode('utf-8')

        environ['PATH_INFO'] = path_info
    with closing(BytesIO()) as stdout, closing(BytesIO()) as stderr:
        new_response = (
            _response
            if _response is not None
            else _response_factory(stdout=stdout, stderr=stderr))
        new_response._http_version = environ['SERVER_PROTOCOL'].split('/')[1]
        new_response._server_version = environ.get('SERVER_SOFTWARE')

        new_request = (
            _request
            if _request is not None
            else _request_factory(environ['wsgi.input'],
                                  environ,
                                  new_response))

        for i in range(getattr(new_request, 'retry_max_count', 3) + 1):
            request = new_request
            response = new_response
            setRequest(request)
            try:
                with load_app(module_info) as new_mod_info:
                    with transaction_pubevents(request, response):
                        response = _publish(request, new_mod_info)

                        user = getSecurityManager().getUser()
                        if user is not None and \
                           user.getUserName() != 'Anonymous User':
                            environ['REMOTE_USER'] = user.getUserName()
                break
            except TransientError:
                if request.supports_retry():
                    new_request = request.retry()
                    new_response = new_request.response
                else:
                    raise
            finally:
                request.close()
                clearRequest()

        # Start the WSGI server response
        status, headers = response.finalize()
        start_response(status, headers)

        if isinstance(response.body, _FILE_TYPES) or \
           IUnboundStreamIterator.providedBy(response.body):
            if 'wsgi.file_wrapper' in environ:
                result = environ['wsgi.file_wrapper'](response.body)
            else:
                result = response.body
        else:
            # If somebody used response.write, that data will be in the
            # response.stdout BytesIO, so we put that before the body.
            result = (response.stdout.getvalue(), response.body)

        for func in response.after_list:
            func()

    # Return the result body iterable.
    return result