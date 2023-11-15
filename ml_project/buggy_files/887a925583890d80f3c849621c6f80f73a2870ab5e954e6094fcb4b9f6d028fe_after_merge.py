    def round(self, freq, ambiguous='raise'):
        return self._round(freq, np.round, ambiguous)