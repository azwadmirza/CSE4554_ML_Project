    def _prepare(self):
        self._n_atoms = self.mobile_atoms.n_atoms

        if not iterable(self.weights) and self.weights == 'mass':
            self.weights = self.ref_atoms.masses
        if self.weights is not None:
            self.weights = np.asarray(self.weights, dtype=np.float64) / np.mean(self.weights)

        current_frame = self.reference.universe.trajectory.ts.frame

        try:
            # Move to the ref_frame
            # (coordinates MUST be stored in case the ref traj is advanced
            # elsewhere or if ref == mobile universe)
            self.reference.universe.trajectory[self.ref_frame]
            self._ref_com = self.ref_atoms.center(self.weights)
            # makes a copy
            self._ref_coordinates = self.ref_atoms.positions - self._ref_com
            if self._groupselections_atoms:
                self._groupselections_ref_coords64 = [(self.reference.
                    select_atoms(*s['reference']).
                    positions.astype(np.float64)) for s in
                    self.groupselections]
        finally:
            # Move back to the original frame
            self.reference.universe.trajectory[current_frame]

        self._ref_coordinates64 = self._ref_coordinates.astype(np.float64)

        if self._groupselections_atoms:
            # Only carry out a rotation if we want to calculate secondary
            # RMSDs.
            # R: rotation matrix that aligns r-r_com, x~-x~com
            #    (x~: selected coordinates, x: all coordinates)
            # Final transformed traj coordinates: x' = (x-x~_com)*R + ref_com
            self._rot = np.zeros(9, dtype=np.float64)  # allocate space
            self._R = self._rot.reshape(3, 3)
        else:
            self._rot = None

        self.rmsd = np.zeros((self.n_frames,
                              3 + len(self._groupselections_atoms)))

        self._pm.format = ("RMSD {rmsd:5.2f} A at frame "
                           "{step:5d}/{numsteps}  [{percentage:5.1f}%]")
        self._mobile_coordinates64 = self.mobile_atoms.positions.copy().astype(np.float64)