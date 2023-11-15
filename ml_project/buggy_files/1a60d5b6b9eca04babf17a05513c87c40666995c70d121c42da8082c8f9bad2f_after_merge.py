    def _grouper(self, tgtkey):
        while self.currkey == tgtkey:
            yield self.currvalue
            try:
                self.currvalue = next(self.it)  # Exit on StopIteration
            except StopIteration:
                return
            self.currkey = self.keyfunc(self.currvalue)