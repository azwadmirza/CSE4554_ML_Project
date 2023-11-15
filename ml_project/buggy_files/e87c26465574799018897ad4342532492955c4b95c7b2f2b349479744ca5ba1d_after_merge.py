def clean_headers(headers):
    """
    Sanitize a dictionary containing HTTP headers of sensitive values.

    :param headers: The headers to sanitize.
    :type headers: dict
    :returns: A list of headers without sensitive information stripped out.
    :rtype: dict
    """
    cleaned_headers = headers.copy()

    authorization_header = headers.get("Authorization")
    if authorization_header:
        sanitized = "****" + authorization_header[-4:]
        cleaned_headers["Authorization"] = sanitized

    return cleaned_headers