    def load_from_statepoint(self, statepoint):
        """Extracts tallies in an OpenMC StatePoint with the data needed to
        compute multi-group cross sections.

        This method is needed to compute cross section data from tallies
        in an OpenMC StatePoint object.

        NOTE: The statepoint must first be linked with an OpenMC Summary object.

        Parameters
        ----------
        statepoint : openmc.StatePoint
            An OpenMC StatePoint object with tally data

        Raises
        ------
        ValueError
            When this method is called with a statepoint that has not been
            linked with a summary object.

        """

        cv.check_type('statepoint', statepoint, openmc.statepoint.StatePoint)

        if statepoint.summary is None:
            msg = 'Unable to load data from a statepoint which has not been ' \
                  'linked with a summary file'
            raise ValueError(msg)

        # Override the domain object that loaded from an OpenMC summary file
        # NOTE: This is necessary for micro cross-sections which require
        # the isotopic number densities as computed by OpenMC
        if self.domain_type == 'cell' or self.domain_type == 'distribcell':
            self.domain = statepoint.summary.get_cell_by_id(self.domain.id)
        elif self.domain_type == 'universe':
            self.domain = statepoint.summary.get_universe_by_id(self.domain.id)
        elif self.domain_type == 'material':
            self.domain = statepoint.summary.get_material_by_id(self.domain.id)
        else:
            msg = 'Unable to load data from a statepoint for domain type {0} ' \
                  'which is not yet supported'.format(self.domain_type)
            raise ValueError(msg)

        # Use tally "slicing" to ensure that tallies correspond to our domain
        # NOTE: This is important if tally merging was used
        if self.domain_type != 'distribcell':
            filters = [self.domain_type]
            filter_bins = [(self.domain.id,)]
        # Distribcell filters only accept single cell - neglect it when slicing
        else:
            filters = []
            filter_bins = []

        # Clear any tallies previously loaded from a statepoint
        if self.loaded_sp:
            self._tallies = None
            self._xs_tally = None
            self._rxn_rate_tally = None
            self._loaded_sp = False

        # Find, slice and store Tallies from StatePoint
        # The tally slicing is needed if tally merging was used
        for tally_type, tally in self.tallies.items():
            sp_tally = statepoint.get_tally(
                tally.scores, tally.filters, tally.nuclides,
                estimator=tally.estimator, exact_filters=True)
            sp_tally = sp_tally.get_slice(
                tally.scores, filters, filter_bins, tally.nuclides)
            sp_tally.sparse = self.sparse
            self.tallies[tally_type] = sp_tally

        self._loaded_sp = True