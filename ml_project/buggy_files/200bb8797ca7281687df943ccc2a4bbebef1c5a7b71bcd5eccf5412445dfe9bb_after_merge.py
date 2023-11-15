    def completedefault(self, text, line, begidx, endidx):
        """Implements tab-completion for text."""
        rl_completion_suppress_append()  # this needs to be called each time
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        if self.completer is None:
            x = []
        else:
            x = [(i[offs:] if " " in i[:-1] else i)
                 for i in self.completer.complete(text, line,
                                                  begidx, endidx,
                                                  ctx=self.ctx)[0]]
        return x