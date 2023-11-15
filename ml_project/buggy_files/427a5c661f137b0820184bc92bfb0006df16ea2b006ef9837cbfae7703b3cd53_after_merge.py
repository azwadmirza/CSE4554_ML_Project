def _append_compressed_format_query(handle):
  # Convert the tuple from urlparse into list so it can be updated in place.
  parsed = list(urlparse.urlparse(handle))
  qsl = urlparse.parse_qsl(parsed[4])
  qsl.append(_COMPRESSED_FORMAT_QUERY)
  # NOTE: Cast to string to avoid urlunparse to deal with mixed types.
  # This happens due to backport of urllib.parse into python2 returning an
  # instance of <class 'future.types.newstr.newstr'>.
  parsed[4] = str(urlencode(qsl))
  return urlparse.urlunparse(parsed)