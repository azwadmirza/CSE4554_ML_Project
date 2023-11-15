    def post(self, url, data, timeout=None):
        """Request an URL.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            data (dict[str, str|int]): A dict of key/value pairs. Note: On py2.7 value is unicode.
            timeout (:obj:`int` | :obj:`float`): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).

        Returns:
          A JSON object.

        """
        urlopen_kwargs = {}

        if timeout is not None:
            urlopen_kwargs['timeout'] = Timeout(read=timeout, connect=self._connect_timeout)

        # Are we uploading files?
        files = False

        for key, val in data.copy().items():
            if isinstance(val, InputFile):
                # Convert the InputFile to urllib3 field format
                data[key] = val.field_tuple
                files = True
            elif isinstance(val, (float, int)):
                # Urllib3 doesn't like floats it seems
                data[key] = str(val)
            elif key == 'media':
                # One media or multiple
                if isinstance(val, InputMedia):
                    # Attach and set val to attached name
                    data[key] = val.to_json()
                    if isinstance(val.media, InputFile):
                        data[val.media.attach] = val.media.field_tuple
                else:
                    # Attach and set val to attached name for all
                    media = []
                    for m in val:
                        media.append(m.to_dict())
                        if isinstance(m.media, InputFile):
                            data[m.media.attach] = m.media.field_tuple
                    data[key] = json.dumps(media)
                files = True

        # Use multipart upload if we're uploading files, otherwise use JSON
        if files:
            result = self._request_wrapper('POST', url, fields=data, **urlopen_kwargs)
        else:
            result = self._request_wrapper('POST', url,
                                           body=json.dumps(data).encode('utf-8'),
                                           headers={'Content-Type': 'application/json'},
                                           **urlopen_kwargs)

        return self._parse(result)