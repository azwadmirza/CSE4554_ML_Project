def _append_compressed_format_query(handle):
  # Convert the tuple from urlparse into list so it can be updated in place.
  parsed = list(urlparse.urlparse(handle))
  qsl = urlparse.parse_qsl(parsed[4])
  qsl.append(_COMPRESSED_FORMAT_QUERY)
  parsed[4] = urlencode(qsl)
  return urlparse.urlunparse(parsed)