    def _add_in_old_format(self, train_perf,
                           incumbent_id, incumbent):
        """
            adds entries to old SMAC2-like trajectory file

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

        with open(self.old_traj_fn, "a") as fp:
            fp.write("%f, %f, %f, %d, %f, %s\n" % (
                ta_time_used,
                train_perf,
                wallclock_time,
                incumbent_id,
                wallclock_time - ta_time_used,
                ", ".join(conf)
            ))