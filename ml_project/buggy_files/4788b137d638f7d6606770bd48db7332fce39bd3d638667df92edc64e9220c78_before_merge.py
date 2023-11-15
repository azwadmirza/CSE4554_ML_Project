    def decode(encoded_uri):
        """Decodes percent-encoded characters in a URI or query string.

        This function models the behavior of `urllib.parse.unquote_plus`,
        albeit in a faster, more straightforward manner.

        Args:
            encoded_uri (str): An encoded URI (full or partial).

        Returns:
            str: A decoded URL. If the URL contains escaped non-ASCII
            characters, UTF-8 is assumed per RFC 3986.

        """

        decoded_uri = encoded_uri

        # PERF(kgriffs): Don't take the time to instantiate a new
        # string unless we have to.
        if '+' in decoded_uri:
            decoded_uri = decoded_uri.replace('+', ' ')

        # Short-circuit if we can
        if '%' not in decoded_uri:
            return decoded_uri

        # NOTE(kgriffs): Clients should never submit a URI that has
        # unescaped non-ASCII chars in them, but just in case they
        # do, let's encode into a non-lossy format.
        decoded_uri = decoded_uri.encode('utf-8')

        # PERF(kgriffs): This was found to be faster than using
        # a regex sub call or list comprehension with a join.
        tokens = decoded_uri.split(b'%')
        decoded_uri = tokens[0]
        for token in tokens[1:]:
            decoded_uri += _HEX_TO_BYTE[token[:2]] + token[2:]

        # Convert back to str
        return decoded_uri.decode('utf-8', 'replace')