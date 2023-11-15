    def _single_frame(self):
        mobile_com = self.mobile_atoms.center(self.weights).astype(np.float64)
        self._mobile_coordinates64[:] = self.mobile_atoms.positions
        self._mobile_coordinates64 -= mobile_com

        self.rmsd[self._frame_index, :2] = self._ts.frame, self._trajectory.time

        if self._groupselections_atoms:
            # superimpose structures: MDAnalysis qcprot needs Nx3 coordinate
            # array with float64 datatype (float32 leads to errors up to 1e-3 in
            # RMSD). Note that R is defined in such a way that it acts **to the
            # left** so that we can easily use broadcasting and save one
            # expensive numpy transposition.

            self.rmsd[self._frame_index, 2] = qcp.CalcRMSDRotationalMatrix(
                self._ref_coordinates_64, self._mobile_coordinates64,
                self._n_atoms, self._rot, self.weights)

            self._R[:, :] = self._rot.reshape(3, 3)
            # Transform each atom in the trajectory (use inplace ops to
            # avoid copying arrays) (Marginally (~3%) faster than
            # "ts.positions[:] = (ts.positions - x_com) * R + ref_com".)
            self._ts.positions[:] -= mobile_com

            # R acts to the left & is broadcasted N times.
            self._ts.positions[:, :] = self._ts.positions * self._R
            self._ts.positions[:] += self._ref_com

            # 2) calculate secondary RMSDs
            for igroup, (refpos, atoms) in enumerate(
                    zip(self._groupselections_ref_coords_64,
                        self._groupselections_atoms), 3):
                self.rmsd[self._frame_index, igroup] = qcp.CalcRMSDRotationalMatrix(
                    refpos, atoms['mobile'].positions.astype(np.float64),
                    atoms['mobile'].n_atoms, None, self.weights)
        else:
            # only calculate RMSD by setting the Rmatrix to None (no need
            # to carry out the rotation as we already get the optimum RMSD)
            self.rmsd[self._frame_index, 2] = qcp.CalcRMSDRotationalMatrix(
                self._ref_coordinates_64, self._mobile_coordinates64,
                self._n_atoms, None, self.weights)

        self._pm.rmsd = self.rmsd[self._frame_index, 2]