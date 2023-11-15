    def get_tally(self, scores=[], filters=[], nuclides=[],
                  name=None, id=None, estimator=None, exact=False):
        """Finds and returns a Tally object with certain properties.

        This routine searches the list of Tallies and returns the first Tally
        found which satisfies all of the input parameters.

        NOTE: If the "exact" parameter is False (default), the input parameters
        do not need to match the complete Tally specification and may only
        represent a subset of the Tally's properties. If the "exact" parameter
        is True then the scores, filters, nuclides and estimator parameters
        must precisely match those of any matching Tally.

        Parameters
        ----------
        scores : list, optional
            A list of one or more score strings (default is []).
        filters : list, optional
            A list of Filter objects (default is []).
        nuclides : list, optional
            A list of Nuclide objects (default is []).
        name : str, optional
            The name specified for the Tally (default is None).
        id : Integral, optional
            The id specified for the Tally (default is None).
        estimator: str, optional
            The type of estimator ('tracklength', 'analog'; default is None).
        exact : bool
            Whether to strictly enforce the match between the parameters and
            the returned tally

        Returns
        -------
        tally : openmc.Tally
            A tally matching the specified criteria

        Raises
        ------
        LookupError
            If a Tally meeting all of the input parameters cannot be found in
            the statepoint.

        """

        tally = None

        # Iterate over all tallies to find the appropriate one
        for tally_id, test_tally in self.tallies.items():

            # Determine if Tally has queried name
            if name and name != test_tally.name:
                continue

            # Determine if Tally has queried id
            if id and id != test_tally.id:
                continue

            # Determine if Tally has queried estimator
            if (estimator or exact) and estimator != test_tally.estimator:
                continue

            # The number of filters, nuclides and scores must exactly match
            if exact:
                if len(scores) != test_tally.num_scores:
                    continue
                if len(nuclides) != test_tally.num_nuclides:
                    continue
                if len(filters) != test_tally.num_filters:
                    continue

            # Determine if Tally has the queried score(s)
            if scores:
                contains_scores = True

                # Iterate over the scores requested by the user
                for score in scores:
                    if score not in test_tally.scores:
                        contains_scores = False
                        break

                if not contains_scores:
                    continue

            # Determine if Tally has the queried Filter(s)
            if filters:
                contains_filters = True

                # Iterate over the Filters requested by the user
                for outer_filter in filters:
                    contains_filters = False

                    # Test if requested filter is a subset of any of the test
                    # tally's filters and if so continue to next filter
                    for inner_filter in test_tally.filters:
                        if inner_filter.is_subset(outer_filter):
                            contains_filters = True
                            break

                    if not contains_filters:
                        break

                if not contains_filters:
                    continue

            # Determine if Tally has the queried Nuclide(s)
            if nuclides:
                contains_nuclides = True

                # Iterate over the Nuclides requested by the user
                for nuclide in nuclides:
                    if nuclide not in test_tally.nuclides:
                        contains_nuclides = False
                        break

                if not contains_nuclides:
                    continue

            # If the current Tally met user's request, break loop and return it
            tally = test_tally
            break

        # If we did not find the Tally, return an error message
        if tally is None:
            raise LookupError('Unable to get Tally')

        return tally