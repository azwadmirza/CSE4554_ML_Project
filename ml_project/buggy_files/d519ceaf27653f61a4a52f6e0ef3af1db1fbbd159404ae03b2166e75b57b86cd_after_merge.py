    def load_data(self, profdatafile):
        """Load profiler data saved by profile/cProfile module"""
        import pstats
        # Fixes spyder-ide/spyder#6220
        try:
            stats_indi = [pstats.Stats(profdatafile), ]
        except (OSError, IOError):
            self.profdata = None
            return
        self.profdata = stats_indi[0]
        
        if self.compare_file is not None:
            # Fixes spyder-ide/spyder#5587
            try:
                stats_indi.append(pstats.Stats(self.compare_file))
            except (OSError, IOError) as e:
                QMessageBox.critical(
                    self, _("Error"),
                    _("Error when trying to load profiler results. "
                      "The error was<br><br>"
                      "<tt>{0}</tt>").format(e))
                self.compare_file = None
        map(lambda x: x.calc_callees(), stats_indi)
        self.profdata.calc_callees()
        self.stats1 = stats_indi
        self.stats = stats_indi[0].stats