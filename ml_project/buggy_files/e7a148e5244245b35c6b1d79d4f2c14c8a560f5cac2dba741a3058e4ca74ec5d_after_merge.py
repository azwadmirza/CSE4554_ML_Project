    def _compute_univariate_density(
        self,
        data_variable,
        common_norm,
        common_grid,
        estimate_kws,
        log_scale,
    ):

        # Initialize the estimator object
        estimator = KDE(**estimate_kws)

        all_data = self.plot_data.dropna()

        if set(self.variables) - {"x", "y"}:
            if common_grid:
                all_observations = self.comp_data.dropna()
                estimator.define_support(all_observations[data_variable])
        else:
            common_norm = False

        densities = {}

        for sub_vars, sub_data in self.iter_data("hue", from_comp_data=True):

            # Extract the data points from this sub set and remove nulls
            sub_data = sub_data.dropna()
            observations = sub_data[data_variable]

            observation_variance = observations.var()
            if math.isclose(observation_variance, 0) or np.isnan(observation_variance):
                msg = "Dataset has 0 variance; skipping density estimate."
                warnings.warn(msg, UserWarning)
                continue

            # Extract the weights for this subset of observations
            if "weights" in self.variables:
                weights = sub_data["weights"]
            else:
                weights = None

            # Estimate the density of observations at this level
            density, support = estimator(observations, weights=weights)

            if log_scale:
                support = np.power(10, support)

            # Apply a scaling factor so that the integral over all subsets is 1
            if common_norm:
                density *= len(sub_data) / len(all_data)

            # Store the density for this level
            key = tuple(sub_vars.items())
            densities[key] = pd.Series(density, index=support)

        return densities