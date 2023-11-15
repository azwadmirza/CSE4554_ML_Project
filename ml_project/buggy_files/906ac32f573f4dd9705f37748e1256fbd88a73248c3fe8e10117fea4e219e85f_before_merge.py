    def recons_codes(self):
        comp_ids, obs_ids, _ = self.group_info
        codes = (ping.codes for ping in self.groupings)
        return decons_obs_group_ids(comp_ids, obs_ids, self.shape, codes, xnull=True)