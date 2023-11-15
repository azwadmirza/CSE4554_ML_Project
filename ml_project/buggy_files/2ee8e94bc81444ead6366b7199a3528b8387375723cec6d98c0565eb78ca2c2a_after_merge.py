    def _single_frame(self):

        box = self._ts.dimensions

        # Update donor-hydrogen pairs if necessary
        if self.update_selections:
            self._donors, self._hydrogens = self._get_dh_pairs()

        # find D and A within cutoff distance of one another
        # min_cutoff = 1.0 as an atom cannot form a hydrogen bond with itself
        d_a_indices, d_a_distances = capped_distance(
            self._donors.positions,
            self._acceptors.positions,
            max_cutoff=self.d_a_cutoff,
            min_cutoff=1.0,
            box=box,
            return_distances=True,
        )

        # Remove D-A pairs more than d_a_cutoff away from one another
        tmp_donors = self._donors[d_a_indices.T[0]]
        tmp_hydrogens = self._hydrogens[d_a_indices.T[0]]
        tmp_acceptors = self._acceptors[d_a_indices.T[1]]

        # Find D-H-A angles greater than d_h_a_angle_cutoff
        d_h_a_angles = np.rad2deg(
            calc_angles(
                tmp_donors.positions,
                tmp_hydrogens.positions,
                tmp_acceptors.positions,
                box=box
            )
        )
        hbond_indices = np.where(d_h_a_angles > self.d_h_a_angle)[0]

        # Retrieve atoms, distances and angles of hydrogen bonds
        hbond_donors = tmp_donors[hbond_indices]
        hbond_hydrogens = tmp_hydrogens[hbond_indices]
        hbond_acceptors = tmp_acceptors[hbond_indices]
        hbond_distances = d_a_distances[hbond_indices]
        hbond_angles = d_h_a_angles[hbond_indices]

        # Store data on hydrogen bonds found at this frame
        self.hbonds[0].extend(np.full_like(hbond_donors, self._ts.frame))
        self.hbonds[1].extend(hbond_donors.indices)
        self.hbonds[2].extend(hbond_hydrogens.indices)
        self.hbonds[3].extend(hbond_acceptors.indices)
        self.hbonds[4].extend(hbond_distances)
        self.hbonds[5].extend(hbond_angles)