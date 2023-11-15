    def escape_xml(self, text):
        for regexp, subsitution in self.MOSES_ESCAPE_XML_REGEXES:
            text = re.sub(regexp, subsitution, text)
        return text