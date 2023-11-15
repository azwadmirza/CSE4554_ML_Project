    def tokenize(self, text, agressive_dash_splits=False, return_str=False):
        """
        Python port of the Moses tokenizer. 
        
        >>> mtokenizer = MosesTokenizer()
        >>> text = u'Is 9.5 or 525,600 my favorite number?'
        >>> print (mtokenizer.tokenize(text, return_str=True))
        Is 9.5 or 525,600 my favorite number ?
        >>> text = u'The https://github.com/jonsafari/tok-tok/blob/master/tok-tok.pl is a website with/and/or slashes and sort of weird : things'
        >>> print (mtokenizer.tokenize(text, return_str=True))
        The https : / / github.com / jonsafari / tok-tok / blob / master / tok-tok.pl is a website with / and / or slashes and sort of weird : things
        >>> text = u'This, is a sentence with weird\xbb symbols\u2026 appearing everywhere\xbf'
        >>> expected = u'This , is a sentence with weird \xbb symbols \u2026 appearing everywhere \xbf'
        >>> assert mtokenizer.tokenize(text, return_str=True) == expected
        
        :param tokens: A single string, i.e. sentence text.
        :type tokens: str
        :param agressive_dash_splits: Option to trigger dash split rules .
        :type agressive_dash_splits: bool
        """
        # Converts input string into unicode.
        text = text_type(text) 
        
        # De-duplicate spaces and clean ASCII junk
        for regexp, subsitution in [self.DEDUPLICATE_SPACE, self.ASCII_JUNK]:
            text = re.sub(regexp, subsitution, text)
        # Strips heading and trailing spaces.
        text = text.strip()
        # Separate special characters outside of IsAlnum character set.
        regexp, subsitution = self.PAD_NOT_ISALNUM
        text = re.sub(regexp, subsitution, text)
        # Aggressively splits dashes
        if agressive_dash_splits:
            regexp, subsitution = self.AGGRESSIVE_HYPHEN_SPLIT
            text = re.sub(regexp, subsitution, text)
        # Replaces multidots with "DOTDOTMULTI" literal strings.
        text = self.replace_multidots(text)
        # Separate out "," except if within numbers e.g. 5,300
        for regexp, subsitution in [self.COMMA_SEPARATE_1, self.COMMA_SEPARATE_2]:
            text = re.sub(regexp, subsitution, text)
        
        # (Language-specific) apostrophe tokenization.
        if self.lang == 'en':
            for regexp, subsitution in self.ENGLISH_SPECIFIC_APOSTROPHE:
                 text = re.sub(regexp, subsitution, text)
        elif self.lang in ['fr', 'it']:
            for regexp, subsitution in self.FR_IT_SPECIFIC_APOSTROPHE:
                text = re.sub(regexp, subsitution, text)
        else:
            regexp, subsitution = self.NON_SPECIFIC_APOSTROPHE
            text = re.sub(regexp, subsitution, text)
        
        # Handles nonbreaking prefixes.
        text = self.handles_nonbreaking_prefixes(text)
        # Cleans up extraneous spaces.
        regexp, subsitution = self.DEDUPLICATE_SPACE
        text = re.sub(regexp,subsitution, text).strip()
        # Restore multidots.
        text = self.restore_multidots(text)
        # Escape XML symbols.
        text = self.escape_xml(text)
        
        return text if return_str else text.split()