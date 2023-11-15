def _get_json_content_from_openml_api(url, error_message, raise_if_error,
                                      data_home):
    """
    Loads json data from the openml api

    Parameters
    ----------
    url : str
        The URL to load from. Should be an official OpenML endpoint

    error_message : str or None
        The error message to raise if an acceptable OpenML error is thrown
        (acceptable error is, e.g., data id not found. Other errors, like 404's
        will throw the native error message)

    raise_if_error : bool
        Whether to raise an error if OpenML returns an acceptable error (e.g.,
        date not found). If this argument is set to False, a None is returned
        in case of acceptable errors. Note that all other errors (e.g., 404)
        will still be raised as normal.

    data_home : str or None
        Location to cache the response. None if no cache is required.

    Returns
    -------
    json_data : json or None
        the json result from the OpenML server if the call was successful;
        None otherwise iff raise_if_error was set to False and the error was
        ``acceptable``
    """
    data_found = True
    try:
        response = _open_openml_url(url, data_home)
    except HTTPError as error:
        # 412 is an OpenML specific error code, indicating a generic error
        # (e.g., data not found)
        if error.code == 412:
            data_found = False
        else:
            raise error
    if not data_found:
        # not in except for nicer traceback
        if raise_if_error:
            raise ValueError(error_message)
        else:
            return None
    json_data = json.loads(response.read().decode("utf-8"))
    response.close()
    return json_data