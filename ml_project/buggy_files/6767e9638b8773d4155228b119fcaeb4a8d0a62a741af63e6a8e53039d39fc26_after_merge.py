    def escape_xml(self, text):
        for regexp, substitution in self.MOSES_ESCAPE_XML_REGEXES:
            text = re.sub(regexp, substitution, text)
        return text