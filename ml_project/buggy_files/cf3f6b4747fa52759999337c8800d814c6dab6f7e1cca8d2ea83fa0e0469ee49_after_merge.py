def default_zpublisher_encoding(value):
    # This is a bit clunky but necessary :-(
    # These modules are imported during the configuration process
    # so a module-level call to getConfiguration in any of them
    # results in getting config data structure without the necessary
    # value in it.
    if PY2:
        # unicode is not acceptable as encoding in HTTP headers:
        value = str(value)
    from ZPublisher import Converters, HTTPRequest, HTTPResponse
    Converters.default_encoding = value
    HTTPRequest.default_encoding = value
    HTTPRequest.HTTPRequest.charset = value
    HTTPResponse.default_encoding = value
    HTTPResponse.HTTPBaseResponse.charset = value
    return value