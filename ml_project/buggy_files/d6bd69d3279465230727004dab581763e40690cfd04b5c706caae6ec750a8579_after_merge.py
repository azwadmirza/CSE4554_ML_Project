    def __init__(self, geometry, settings, chain_file=None, prev_results=None,
                 diff_burnable_mats=False, fission_q=None,
                 dilute_initial=1.0e3):
        super().__init__(chain_file, fission_q, dilute_initial)
        self.round_number = False
        self.prev_res = None
        self.settings = settings
        self.geometry = geometry
        self.diff_burnable_mats = diff_burnable_mats

        # Differentiate burnable materials with multiple instances
        if self.diff_burnable_mats:
            self._differentiate_burnable_mats()

        # Clear out OpenMC, create task lists, distribute
        openmc.reset_auto_ids()
        self.burnable_mats, volume, nuclides = self._get_burnable_mats()
        self.local_mats = _distribute(self.burnable_mats)

        # Generate map from local materials => material index
        self._mat_index_map = {
            lm: self.burnable_mats.index(lm) for lm in self.local_mats}

        if prev_results is not None:
            # Reload volumes into geometry
            prev_results[-1].transfer_volumes(geometry)

            # Store previous results in operator
            # Distribute reaction rates according to those tracked
            # on this process
            if comm.size == 1:
                self.prev_res = prev_results
            else:
                self.prev_res = ResultsList()
                mat_indexes = _distribute(range(len(self.burnable_mats)))
                for res_obj in prev_results:
                    new_res = res_obj.distribute(self.local_mats, mat_indexes)
                    self.prev_res.append(new_res)

        # Determine which nuclides have incident neutron data
        self.nuclides_with_data = self._get_nuclides_with_data()

        # Select nuclides with data that are also in the chain
        self._burnable_nucs = [nuc.name for nuc in self.chain.nuclides
                               if nuc.name in self.nuclides_with_data]

        # Extract number densities from the geometry / previous depletion run
        self._extract_number(self.local_mats, volume, nuclides, self.prev_res)

        # Create reaction rates array
        self.reaction_rates = ReactionRates(
            self.local_mats, self._burnable_nucs, self.chain.reactions)

        # Get classes to assist working with tallies
        self._rate_helper = DirectReactionRateHelper(
            self.reaction_rates.n_nuc, self.reaction_rates.n_react)
        self._energy_helper = ChainFissionHelper()