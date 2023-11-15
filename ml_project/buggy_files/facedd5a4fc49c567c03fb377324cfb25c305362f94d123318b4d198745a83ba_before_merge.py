    def plot_diagnostics(self, variable=0, lags=10, fig=None, figsize=None,
                         truncate_endog_names=24):
        """
        Diagnostic plots for standardized residuals of one endogenous variable

        Parameters
        ----------
        variable : int, optional
            Index of the endogenous variable for which the diagnostic plots
            should be created. Default is 0.
        lags : int, optional
            Number of lags to include in the correlogram. Default is 10.
        fig : Figure, optional
            If given, subplots are created in this figure instead of in a new
            figure. Note that the 2x2 grid will be created in the provided
            figure using `fig.add_subplot()`.
        figsize : tuple, optional
            If a figure is created, this argument allows specifying a size.
            The tuple is (width, height).

        Returns
        -------
        Figure
            Figure instance with diagnostic plots

        See Also
        --------
        statsmodels.graphics.gofplots.qqplot
        statsmodels.graphics.tsaplots.plot_acf

        Notes
        -----
        Produces a 2x2 plot grid with the following plots (ordered clockwise
        from top left):

        1. Standardized residuals over time
        2. Histogram plus estimated density of standardized residuals, along
           with a Normal(0,1) density plotted for reference.
        3. Normal Q-Q plot, with Normal reference line.
        4. Correlogram
        """
        from statsmodels.graphics.utils import _import_mpl, create_mpl_fig
        _import_mpl()
        fig = create_mpl_fig(fig, figsize)
        # Eliminate residuals associated with burned or diffuse likelihoods
        d = np.maximum(self.loglikelihood_burn, self.nobs_diffuse)

        # If given a variable name, find the index
        if isinstance(variable, str):
            variable = self.model.endog_names.index(variable)

        # Get residuals
        if hasattr(self.data, 'dates') and self.data.dates is not None:
            ix = self.data.dates[d:]
        else:
            ix = np.arange(self.nobs - d)
        resid = pd.Series(
            self.filter_results.standardized_forecasts_error[variable, d:],
            index=ix)

        # Top-left: residuals vs time
        ax = fig.add_subplot(221)
        resid.dropna().plot(ax=ax)
        ax.hlines(0, ix[0], ix[-1], alpha=0.5)
        ax.set_xlim(ix[0], ix[-1])
        name = self.model.endog_names[variable]
        if len(name) > truncate_endog_names:
            name = name[:truncate_endog_names - 3] + '...'
        ax.set_title(f'Standardized residual for "{name}"')

        # Top-right: histogram, Gaussian kernel density, Normal density
        # Can only do histogram and Gaussian kernel density on the non-null
        # elements
        resid_nonmissing = resid.dropna()
        ax = fig.add_subplot(222)

        # gh5792: Remove  except after support for matplotlib>2.1 required
        try:
            ax.hist(resid_nonmissing, density=True, label='Hist')
        except AttributeError:
            ax.hist(resid_nonmissing, normed=True, label='Hist')

        from scipy.stats import gaussian_kde, norm
        kde = gaussian_kde(resid_nonmissing)
        xlim = (-1.96*2, 1.96*2)
        x = np.linspace(xlim[0], xlim[1])
        ax.plot(x, kde(x), label='KDE')
        ax.plot(x, norm.pdf(x), label='N(0,1)')
        ax.set_xlim(xlim)
        ax.legend()
        ax.set_title('Histogram plus estimated density')

        # Bottom-left: QQ plot
        ax = fig.add_subplot(223)
        from statsmodels.graphics.gofplots import qqplot
        qqplot(resid_nonmissing, line='s', ax=ax)
        ax.set_title('Normal Q-Q')

        # Bottom-right: Correlogram
        ax = fig.add_subplot(224)
        from statsmodels.graphics.tsaplots import plot_acf
        plot_acf(resid, ax=ax, lags=lags)
        ax.set_title('Correlogram')

        ax.set_ylim(-1, 1)

        return fig