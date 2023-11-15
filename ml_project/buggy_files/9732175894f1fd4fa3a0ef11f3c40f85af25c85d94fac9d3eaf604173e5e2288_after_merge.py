    def debug_string(self):
        """This provides a progress notification for the algorithm.

        For each bracket, the algorithm will output a string as follows:

            Bracket(Max Size (n)=5, Milestone (r)=33, completed=14.6%):
            {PENDING: 2, RUNNING: 3, TERMINATED: 2}

        "Max Size" indicates the max number of pending/running experiments
        set according to the Hyperband algorithm.

        "Milestone" indicates the iterations a trial will run for before
        the next halving will occur.

        "Completed" indicates an approximate progress metric. Some brackets,
        like ones that are unfilled, will not reach 100%.
        """
        out = "Using HyperBand: "
        out += "num_stopped={} total_brackets={}".format(
            self._num_stopped, sum(len(band) for band in self._hyperbands))
        for i, band in enumerate(self._hyperbands):
            out += "\nRound #{}:".format(i)
            for bracket in band:
                if bracket:
                    out += "\n  {}".format(bracket)
        return out