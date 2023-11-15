    def os(self, s):
        """
        Write a string to the output file or stream.

        All output produced by leoAtFile module goes here.
        """
        at = self
        if s.startswith(self.underindentEscapeString):
            try:
                junk, s = at.parseUnderindentTag(s)
            except Exception:
                at.exception("exception writing:" + s)
                return
        s = g.toUnicode(s, at.encoding)
        at.outputList.append(s)