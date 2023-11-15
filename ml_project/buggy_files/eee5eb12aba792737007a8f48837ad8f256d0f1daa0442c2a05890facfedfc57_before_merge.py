    def get_name_as_unicode(self):
        """ Returns the info['name'] field as Unicode string.
        @return Unicode string. """
        if "name.utf-8" in self.metainfo["info"]:
            # There is an utf-8 encoded name.  We assume that it is
            # correctly encoded and use it normally
            try:
                return ensure_unicode(self.metainfo["info"]["name.utf-8"], "UTF-8")
            except UnicodeError:
                pass

        if "name" in self.metainfo["info"]:
            # Try to use the 'encoding' field.  If it exists, it
            # should contain something like 'utf-8'
            if "encoding" in self.metainfo:
                try:
                    return ensure_unicode(self.metainfo["info"]["name"], self.metainfo["encoding"])
                except UnicodeError:
                    pass
                except LookupError:
                    # Some encodings are not supported by python.  For
                    # instance, the MBCS codec which is used by
                    # Windows is not supported (Jan 2010)
                    pass

            # Try to convert the names in path to unicode, without
            # specifying the encoding
            try:
                return text_type(self.metainfo["info"]["name"])
            except UnicodeError:
                pass

            # Try to convert the names in path to unicode, assuming
            # that it was encoded as utf-8
            try:
                return ensure_unicode(self.metainfo["info"]["name"], "UTF-8")
            except UnicodeError:
                pass

            # Convert the names in path to unicode by replacing out
            # all characters that may -even remotely- cause problems
            # with the '?' character
            try:
                def filter_characters(name):
                    def filter_character(char):
                        if 0 < ord(char) < 128:
                            return char
                        else:
                            self._logger.debug("Bad character filter %s, isalnum? %s", ord(char), char.isalnum())
                            return u"?"
                    return u"".join([filter_character(char) for char in name])
                return text_type(filter_characters(self.metainfo["info"]["name"]))
            except UnicodeError:
                pass

        # We failed.  Returning an empty string
        return u""