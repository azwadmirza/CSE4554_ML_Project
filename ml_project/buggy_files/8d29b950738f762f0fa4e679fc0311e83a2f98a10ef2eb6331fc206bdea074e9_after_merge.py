  def _GetVirusTotalJSONResponse(self, hashes):
    """Makes a request to VirusTotal for information about hashes.

    Args:
      A list of file hashes (strings).

    Returns:
      The decoded JSON response from the VirusTotal API for the hashes.

    Raises:
      requests.ConnectionError: If it was not possible to connect to
                                VirusTotal.
      requests.exceptions.HTTPError: If the VirusTotal server returned an
                                     error code.
    """
    resource_string = u', '.join(hashes)
    params = {u'apikey': self._api_key, u'resource': resource_string}
    try:
      response = requests.get(self._VIRUSTOTAL_API_REPORT_URL, params=params)
      response.raise_for_status()
    except requests.ConnectionError as exception:
      error_string = u'Unable to connect to VirusTotal: {0:s}'.format(
          exception)
      raise errors.ConnectionError(error_string)
    except requests.HTTPError as exception:
      error_string = u'VirusTotal returned a HTTP error: {0:s}'.format(
          exception)
      raise errors.ConnectionError(error_string)
    json_response = response.json()
    return json_response