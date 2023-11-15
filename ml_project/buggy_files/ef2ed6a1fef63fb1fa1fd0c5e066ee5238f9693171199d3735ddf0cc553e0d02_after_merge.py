    def _initialize_index(self, data_file, regions):
        DLE = data_file.ds.domain_left_edge
        DRE = data_file.ds.domain_right_edge
        self._float_type = data_file.ds._header.float_type
        if self.index_ptype == "all":
            count = sum(data_file.total_particles.values())
            return self._get_morton_from_position(
                data_file, count, 0, regions, DLE, DRE)
        else:
            idpos = self._ptypes.index(self.index_ptype)
            count = data_file.total_particles.get(self.index_ptype)
            account = [0] + [data_file.total_particles.get(ptype)
                             for ptype in self._ptypes]
            account = np.cumsum(account)
            return self._get_morton_from_position(
                data_file, account, account[idpos], regions, DLE, DRE)