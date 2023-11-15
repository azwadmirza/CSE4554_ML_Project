    def _geom(self):
        """Keeps the GEOS geometry in synch with the context."""
        gtag = self.gtag()
        if gtag != self._gtag or self._is_empty:
            self.empty()
            self.__geom__, n = self.factory(self.context)
        self._gtag = gtag
        return self.__geom__