    def writeAsisNode(self, p):
        '''Write the p's node to an @asis file.'''
        at = self
        # Write the headline only if it starts with '@@'.
        s = p.h
        if g.match(s, 0, "@@"):
            s = s[2:]
            if s:
                at.outputFile.write(s)
        # Write the body.
        s = p.b
        if s:
            s = g.toEncodedString(s, at.encoding, reportErrors=True)
            at.outputStringWithLineEndings(s)