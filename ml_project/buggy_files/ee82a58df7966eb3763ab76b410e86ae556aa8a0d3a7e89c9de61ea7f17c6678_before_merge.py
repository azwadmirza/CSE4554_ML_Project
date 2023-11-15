    def plot_distribution(self, ax=None, exog_values=None):
        """
        Plot the fitted probabilities of endog in an nominal model,
        for specifed values of the predictors.

        Parameters
        ----------
        ax : Matplotlib axes instance
            An axes on which to draw the graph.  If None, new
            figure and axes objects are created
        exog_values : array-like
            A list of dictionaries, with each dictionary mapping
            variable names to values at which the variable is held
            fixed.  The values P(endog=y | exog) are plotted for all
            possible values of y, at the given exog value.  Variables
            not included in a dictionary are held fixed at the mean
            value.

        Example:
        --------
        We have a model with covariates 'age' and 'sex', and wish to
        plot the probabilities P(endog=y | exog) for males (sex=0) and
        for females (sex=1), as separate paths on the plot.  Since
        'age' is not included below in the map, it is held fixed at
        its mean value.

        >>> ex = [{"sex": 1}, {"sex": 0}]
        >>> rslt.distribution_plot(exog_values=ex)
        """

        from statsmodels.graphics import utils as gutils

        if ax is None:
            fig, ax = gutils.create_mpl_ax(ax)
        else:
            fig = ax.get_figure()

        # If no covariate patterns are specified, create one with all
        # variables set to their mean values.
        if exog_values is None:
            exog_values = [{}, ]

        link = self.model.family.link.inverse
        ncut = self.model.family.ncut

        k = int(self.model.exog.shape[1] / ncut)
        exog_means = self.model.exog.mean(0)[0:k]
        exog_names = self.model.exog_names[0:k]
        exog_names = [x.split("[")[0] for x in exog_names]

        params = np.reshape(self.params,
                            (ncut, len(self.params) / ncut))

        for ev in exog_values:

            exog = exog_means.copy()

            for k in ev.keys():
                if k not in exog_names:
                    raise ValueError("%s is not a variable in the model"
                                     % k)

                ii = exog_names.index(k)
                exog[ii] = ev[k]

            lpr = np.dot(params, exog)
            pr = link(lpr)
            pr = np.r_[pr, 1 - pr.sum()]

            ax.plot(self.model.endog_values, pr, 'o-')

        ax.set_xlabel("Response value")
        ax.set_ylabel("Probability")
        ax.set_xticks(self.model.endog_values)
        ax.set_xticklabels(self.model.endog_values)
        ax.set_ylim(0, 1)

        return fig