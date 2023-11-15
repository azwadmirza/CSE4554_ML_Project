    def plot_simultaneous(self, comparison_name=None, ax=None, figsize=(10,6),
                          xlabel=None, ylabel=None):
        """Plot a universal confidence interval of each group mean

        Visiualize significant differences in a plot with one confidence
        interval per group instead of all pairwise confidence intervals.

        Parameters
        ----------
        comparison_name : string, optional
            if provided, plot_intervals will color code all groups that are
            significantly different from the comparison_name red, and will
            color code insignificant groups gray. Otherwise, all intervals will
            just be plotted in black.
        ax : matplotlib axis, optional
            An axis handle on which to attach the plot.
        figsize : tuple, optional
            tuple for the size of the figure generated
        xlabel : string, optional
            Name to be displayed on x axis
        ylabel : string, optional
            Name to be displayed on y axis

        Returns
        -------
        fig : Matplotlib Figure object
            handle to figure object containing interval plots

        Notes
        -----
        Multiple comparison tests are nice, but lack a good way to be
        visualized. If you have, say, 6 groups, showing a graph of the means
        between each group will require 15 confidence intervals.
        Instead, we can visualize inter-group differences with a single
        interval for each group mean. Hochberg et al. [1] first proposed this
        idea and used Tukey's Q critical value to compute the interval widths.
        Unlike plotting the differences in the means and their respective
        confidence intervals, any two pairs can be compared for significance
        by looking for overlap.

        References
        ----------
        .. [*] Hochberg, Y., and A. C. Tamhane. Multiple Comparison Procedures.
               Hoboken, NJ: John Wiley & Sons, 1987.

        Examples
        --------
        >>> from statsmodels.examples.try_tukey_hsd import cylinders, cyl_labels
        >>> from statsmodels.stats.multicomp import MultiComparison
        >>> cardata = MultiComparison(cylinders, cyl_labels)
        >>> results = cardata.tukeyhsd()
        >>> results.plot_simultaneous()
        <matplotlib.figure.Figure at 0x...>

        This example shows an example plot comparing significant differences
        in group means. Significant differences at the alpha=0.05 level can be
        identified by intervals that do not overlap (i.e. USA vs Japan,
        USA vs Germany).

        >>> results.plot_simultaneous(comparison_name="USA")
        <matplotlib.figure.Figure at 0x...>

        Optionally provide one of the group names to color code the plot to
        highlight group means different from comparison_name.

        """
        fig, ax1 = utils.create_mpl_ax(ax)
        if figsize is not None:
            fig.set_size_inches(figsize)
        if getattr(self, 'halfwidths', None) is None:
            self._simultaneous_ci()
        means = self._multicomp.groupstats.groupmean


        sigidx = []
        nsigidx = []
        minrange = [means[i] - self.halfwidths[i] for i in range(len(means))]
        maxrange = [means[i] + self.halfwidths[i] for i in range(len(means))]

        if comparison_name is None:
            ax1.errorbar(means, lrange(len(means)), xerr=self.halfwidths,
                         marker='o', linestyle='None', color='k', ecolor='k')
        else:
            if comparison_name not in self.groupsunique:
                raise ValueError('comparison_name not found in group names.')
            midx = np.where(self.groupsunique==comparison_name)[0]
            for i in range(len(means)):
                if self.groupsunique[i] == comparison_name:
                    continue
                if (min(maxrange[i], maxrange[midx]) -
                                         max(minrange[i], minrange[midx]) < 0):
                    sigidx.append(i)
                else:
                    nsigidx.append(i)
            #Plot the master comparison
            ax1.errorbar(means[midx], midx, xerr=self.halfwidths[midx],
                         marker='o', linestyle='None', color='b', ecolor='b')
            ax1.plot([minrange[midx]]*2, [-1, self._multicomp.ngroups],
                     linestyle='--', color='0.7')
            ax1.plot([maxrange[midx]]*2, [-1, self._multicomp.ngroups],
                     linestyle='--', color='0.7')
            #Plot those that are significantly different
            if len(sigidx) > 0:
                ax1.errorbar(means[sigidx], sigidx,
                             xerr=self.halfwidths[sigidx], marker='o',
                             linestyle='None', color='r', ecolor='r')
            #Plot those that are not significantly different
            if len(nsigidx) > 0:
                ax1.errorbar(means[nsigidx], nsigidx,
                             xerr=self.halfwidths[nsigidx], marker='o',
                             linestyle='None', color='0.5', ecolor='0.5')

        ax1.set_title('Multiple Comparisons Between All Pairs (Tukey)')
        r = np.max(maxrange) - np.min(minrange)
        ax1.set_ylim([-1, self._multicomp.ngroups])
        ax1.set_xlim([np.min(minrange) - r / 10., np.max(maxrange) + r / 10.])
        ax1.set_yticklabels(np.insert(self.groupsunique.astype(str), 0, ''))
        ax1.set_yticks(np.arange(-1, len(means)+1))
        ax1.set_xlabel(xlabel if xlabel is not None else '')
        ax1.set_ylabel(ylabel if ylabel is not None else '')
        return fig