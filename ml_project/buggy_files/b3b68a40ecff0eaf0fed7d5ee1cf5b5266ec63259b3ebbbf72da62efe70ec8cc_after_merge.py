    def get_encoding(self):
        """Parse the font encoding

        The Type1 font encoding maps character codes to character names. These character names could either be standard
        Adobe glyph names, or character names associated with custom CharStrings for this font. A CharString is a
        sequence of operations that describe how the character should be drawn.
        Currently, this function returns '' (empty string) for character names that are associated with a CharStrings.

        References: http://wwwimages.adobe.com/content/dam/Adobe/en/devnet/font/pdfs/T1_SPEC.pdf

        :returns mapping of character identifiers (cid's) to unicode characters
        """
        while 1:
            try:
                (cid, name) = self.nextobject()
            except PSEOF:
                break
            try:
                self._cid2unicode[cid] = name2unicode(name)
            except KeyError as e:
                log.debug(str(e))
        return self._cid2unicode