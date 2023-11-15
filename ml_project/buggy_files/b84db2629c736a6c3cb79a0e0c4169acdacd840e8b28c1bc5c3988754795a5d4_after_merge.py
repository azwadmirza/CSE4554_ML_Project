    def writeAsisNode(self, p):
        '''Write the p's node to an @asis file.'''
        at = self
        
        def put(s):
            """Append s to self.output_list."""
            # #1480: Avoid calling at.os().
            s = g.toUnicode(s, at.encoding, reportErrors=True)
            at.outputList.append(s)

        # Write the headline only if it starts with '@@'.
        s = p.h
        if g.match(s, 0, "@@"):
            s = s[2:]
            if s:
                put('\n') # Experimental.
                put(s)
                put('\n')
        # Write the body.
        s = p.b
        if s:
            put(s)