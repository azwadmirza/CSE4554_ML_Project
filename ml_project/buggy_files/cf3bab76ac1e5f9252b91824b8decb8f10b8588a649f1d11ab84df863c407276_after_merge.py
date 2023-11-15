    def _get_all_files_as_unicode_with_length(self):
        """ Get a generator for files in the torrent def. No filtering
        is possible and all tricks are allowed to obtain a unicode
        list of filenames.
        @return A unicode filename generator.
        """
        if self.metainfo and "files" in self.metainfo["info"]:
            # Multi-file torrent
            join = os.path.join
            files = self.metainfo["info"]["files"]

            for file_dict in files:
                if "path.utf-8" in file_dict:
                    # This file has an utf-8 encoded list of elements.
                    # We assume that it is correctly encoded and use
                    # it normally
                    try:
                        yield (join(*[ensure_unicode(element, "UTF-8") for element in file_dict["path.utf-8"]]),
                               file_dict["length"])
                        continue
                    except UnicodeError:
                        pass

                if "path" in file_dict:
                    # Try to use the 'encoding' field.  If it exists,
                    # it should contain something like 'utf-8'
                    if "encoding" in self.metainfo:
                        encoding = self.metainfo["encoding"]
                        try:
                            yield (join(*[ensure_unicode(element, encoding) for element in file_dict["path"]]),
                                   file_dict["length"])
                            continue
                        except UnicodeError:
                            pass
                        except LookupError:
                            # Some encodings are not supported by
                            # python.  For instance, the MBCS codec
                            # which is used by Windows is not
                            # supported (Jan 2010)
                            pass

                    # Try to convert the names in path to unicode,
                    # without specifying the encoding
                    try:
                        yield join(*[text_type(element) for element in file_dict["path"]]), file_dict["length"]
                        continue
                    except UnicodeError:
                        pass

                    # Try to convert the names in path to unicode,
                    # assuming that it was encoded as utf-8
                    try:
                        yield (join(*[ensure_unicode(element, "UTF-8") for element in file_dict["path"]]),
                               file_dict["length"])
                        continue
                    except UnicodeError:
                        pass

                    # Convert the names in path to unicode by
                    # replacing out all characters that may -even
                    # remotely- cause problems with the '?' character
                    try:
                        def filter_characters(name):
                            def filter_character(char):
                                if 0 < ord(char) < 128:
                                    return char
                                else:
                                    self._logger.debug(
                                        "Bad character filter %s, isalnum? %s", ord(char), char.isalnum())
                                    return u"?"
                            return u"".join([filter_character(char) for char in name])
                        yield (join(*[text_type(filter_characters(element)) for element in file_dict["path"]]),
                               file_dict["length"])
                        continue
                    except UnicodeError:
                        pass

        elif self.metainfo:
            # Single-file torrent
            yield self.get_name_as_unicode(), self.metainfo["info"]["length"]