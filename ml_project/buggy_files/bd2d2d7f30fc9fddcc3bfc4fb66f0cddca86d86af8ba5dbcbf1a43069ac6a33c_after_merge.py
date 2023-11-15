    def fetch(self):
        '''Fetches progress and available results from background'''
        while self.pipe.poll(0):
            try:
                datum = self.pipe.recv()
            except EOFError:
                logger.debug("Process canceled be user.")
                self._canceled = True
                self.process = None
                return
            else:
                if isinstance(datum, StopIteration):
                    self._completed = True
                    self.process = None
                    return
                elif isinstance(datum, EarlyCancellationError):
                    self._canceled = True
                    self.process = None
                    return
                elif isinstance(datum, Exception):
                    raise datum
                else:
                    yield datum