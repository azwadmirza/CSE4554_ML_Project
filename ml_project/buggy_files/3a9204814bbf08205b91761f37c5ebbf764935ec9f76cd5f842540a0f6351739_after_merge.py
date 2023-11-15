    def _add_in_aclib_format(self, train_perf,
                             incumbent_id, incumbent):
        """
            adds entries to AClib2-like trajectory file

            Parameters
            ----------
            train_perf: float
                estimated performance on training (sub)set 
            incumbent_id: int
                id of incumbent
            incumbent: Configuration()
                current incumbent configuration
        """

        conf = []
        for p in incumbent:
            if not incumbent[p] is None:
                conf.append("%s='%s'" % (p, repr(incumbent[p])))

        ta_time_used = self.stats.ta_time_used
        wallclock_time = self.stats.get_used_wallclock_time()

        traj_entry = {"cpu_time": ta_time_used,
                      "total_cpu_time": None,  # TODO: fix this
                      "wallclock_time": wallclock_time,
                      "evaluations": self.stats.ta_runs,
                      "cost": train_perf,
                      "incumbent": conf
                      }

        with open(self.aclib_traj_fn, "a") as fp:
            json.dump(traj_entry, fp)
            fp.write("\n")