    def run(self, **kwargs):
        """Analyze trajectory and produce timeseries"""
        h_list = MDAnalysis.analysis.hbonds.HydrogenBondAnalysis(self.universe,
                                                                 self.selection1,
                                                                 self.selection2,
                                                                 distance=3.5,
                                                                 angle=120.0)
        h_list.run(**kwargs)
        self.timeseries = self._getGraphics(h_list.timeseries, self.t0,
                                            self.tf, self.dtmax)