    def _single_frame(self):
        index = self._frame_index
        mobile_com = self.mobile_atoms.center(self._weights)
        mobile_coordinates = self.mobile_atoms.positions - mobile_com
        mobile_atoms, self.rmsd[index] = _fit_to(mobile_coordinates,
                                                 self._ref_coordinates,
                                                 self.mobile,
                                                 mobile_com,
                                                 self._ref_com, self._weights)
        # write whole aligned input trajectory system
        self._writer.write(mobile_atoms)