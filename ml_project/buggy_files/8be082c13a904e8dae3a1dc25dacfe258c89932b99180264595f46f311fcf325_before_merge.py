def _download_file(url, required_length, STRICT_REQUIRED_LENGTH=True):
  """
  <Purpose>
    Given the url and length of the desired file, this function opens a
    connection to 'url' and downloads the file while ensuring its length
    matches 'required_length' if 'STRICT_REQUIRED_LENGH' is True (If False,
    the file's length is not checked and a slow retrieval exception is raised
    if the downloaded rate falls below the acceptable rate).

  <Arguments>
    url:
      A URL string that represents the location of the file.

    required_length:
      An integer value representing the length of the file.

    STRICT_REQUIRED_LENGTH:
      A Boolean indicator used to signal whether we should perform strict
      checking of required_length. True by default. We explicitly set this to
      False when we know that we want to turn this off for downloading the
      timestamp metadata, which has no signed required_length.

  <Side Effects>
    A file object is created on disk to store the contents of 'url'.

  <Exceptions>
    tuf.exceptions.DownloadLengthMismatchError, if there was a
    mismatch of observed vs expected lengths while downloading the file.

    securesystemslib.exceptions.FormatError, if any of the arguments are
    improperly formatted.

    Any other unforeseen runtime exception.

  <Returns>
    A file object that points to the contents of 'url'.
  """

  # Do all of the arguments have the appropriate format?
  # Raise 'securesystemslib.exceptions.FormatError' if there is a mismatch.
  securesystemslib.formats.URL_SCHEMA.check_match(url)
  tuf.formats.LENGTH_SCHEMA.check_match(required_length)

  # 'url.replace('\\', '/')' is needed for compatibility with Windows-based
  # systems, because they might use back-slashes in place of forward-slashes.
  # This converts it to the common format.  unquote() replaces %xx escapes in a
  # url with their single-character equivalent.  A back-slash may be encoded as
  # %5c in the url, which should also be replaced with a forward slash.
  url = six.moves.urllib.parse.unquote(url).replace('\\', '/')
  logger.info('Downloading: ' + repr(url))

  # This is the temporary file that we will return to contain the contents of
  # the downloaded file.
  temp_file = tempfile.TemporaryFile()

  try:
    # Use a different requests.Session per schema+hostname combination, to
    # reuse connections while minimizing subtle security issues.
    parsed_url = six.moves.urllib.parse.urlparse(url)

    if not parsed_url.scheme or not parsed_url.hostname:
      raise tuf.exceptions.URLParsingError(
          'Could not get scheme and hostname from URL: ' + url)

    session_index = parsed_url.scheme + '+' + parsed_url.hostname

    logger.debug('url: ' + url)
    logger.debug('session index: ' + session_index)

    session = _sessions.get(session_index)

    if not session:
      session = requests.Session()
      _sessions[session_index] = session

      # Attach some default headers to every Session.
      requests_user_agent = session.headers['User-Agent']
      # Follows the RFC: https://tools.ietf.org/html/rfc7231#section-5.5.3
      tuf_user_agent = 'tuf/' + tuf.__version__ + ' ' + requests_user_agent
      session.headers.update({
          # Tell the server not to compress or modify anything.
          # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding#Directives
          'Accept-Encoding': 'identity',
          # The TUF user agent.
          'User-Agent': tuf_user_agent})

      logger.debug('Made new session for ' + session_index)

    else:
      logger.debug('Reusing session for ' + session_index)

    # Get the requests.Response object for this URL.
    #
    # Always stream to control how requests are downloaded:
    # http://docs.python-requests.org/en/master/user/advanced/#body-content-workflow
    #
    # We will always manually close Responses, so no need for a context
    # manager.
    #
    # Always set the timeout. This timeout value is interpreted by requests as:
    #  - connect timeout (max delay before first byte is received)
    #  - read (gap) timeout (max delay between bytes received)
    # These are NOT overall/total, wall-clock timeouts for any single read.
    # http://docs.python-requests.org/en/master/user/advanced/#timeouts
    response = session.get(
        url, stream=True, timeout=tuf.settings.SOCKET_TIMEOUT)

    # Check response status.
    response.raise_for_status()

    # We ask the server about how big it thinks this file should be.
    reported_length = _get_content_length(response)

    # Then, we check whether the required length matches the reported length.
    _check_content_length(reported_length, required_length,
                          STRICT_REQUIRED_LENGTH)

    # Download the contents of the URL, up to the required length, to a
    # temporary file, and get the total number of downloaded bytes.
    total_downloaded, average_download_speed = \
      _download_fixed_amount_of_data(response, temp_file, required_length)

    # Does the total number of downloaded bytes match the required length?
    _check_downloaded_length(total_downloaded, required_length,
                             STRICT_REQUIRED_LENGTH=STRICT_REQUIRED_LENGTH,
                             average_download_speed=average_download_speed)

  except Exception:
    # Close 'temp_file'.  Any written data is lost.
    temp_file.close()
    logger.exception('Could not download URL: ' + repr(url))
    raise

  else:
    return temp_file