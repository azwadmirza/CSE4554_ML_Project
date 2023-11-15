    def parse_leo_file(self, theFile, inputFileName, silent, inClipboard, s=None):
        c = self.c
        try:
            if g.isPython3:
                if theFile:
                    # Use the open binary file, opened by the caller.
                    s = theFile.read() # isinstance(s, bytes)
                    s = self.cleanSaxInputString(s)
                    theFile = BytesIO(s)
                else:
                    s = str(s, encoding='utf-8')
                    s = self.cleanSaxInputString(s)
                    theFile = StringIO(s)
            else:
                if theFile: s = theFile.read()
                s = self.cleanSaxInputString(s)
                theFile = cStringIO.StringIO(s)
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_external_ges, 1)
                # Include external general entities, esp. xml-stylesheet lines.
            if 0: # Expat does not read external features.
                parser.setFeature(xml.sax.handler.feature_external_pes, 1)
                    # Include all external parameter entities
                    # Hopefully the parser can figure out the encoding from the <?xml> element.
            # It's very hard to do anything meaningful wih an exception.
            handler = SaxContentHandler(c, inputFileName, silent, inClipboard)
            parser.setContentHandler(handler)
            parser.parse(theFile) # expat does not support parseString
            # g.trace('parsing done')
            sax_node = handler.getRootNode()
        except Exception:
            g.error('error parsing', inputFileName)
            g.es_exception()
            sax_node = None
        return sax_node