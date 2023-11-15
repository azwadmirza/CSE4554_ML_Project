    def set_position(self, new_position: (float, float)):
        self.clear_spatial_hashes()
        self._position[0] = new_position[0]
        self._position[1] = new_position[1]
        self._point_list_cache = None