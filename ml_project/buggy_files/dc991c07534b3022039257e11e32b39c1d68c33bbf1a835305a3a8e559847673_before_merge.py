    def group_info(self):
        ngroups = self.ngroups
        obs_group_ids = np.arange(ngroups, dtype='int64')
        rep = np.diff(np.r_[0, self.bins])

        if ngroups == len(self.bins):
            comp_ids = np.repeat(np.arange(ngroups, dtype='int64'), rep)
        else:
            comp_ids = np.repeat(np.r_[-1, np.arange(ngroups, dtype='int64')], rep)

        return comp_ids, obs_group_ids, ngroups