    def floor(self, freq, ambiguous='raise'):
        return self._round(freq, np.floor, ambiguous)