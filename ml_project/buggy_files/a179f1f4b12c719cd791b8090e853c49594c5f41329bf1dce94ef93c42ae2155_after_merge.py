    def analyze_clusters(self, **kwargs):
        """
        This function analyzes the clusters according to the provided method

        :param kwargs: a dictionary of cluster-analysis-specific parameters
        :type kwargs: `dict`
        :return: assigned_clean_by_class, an array of arrays that contains what data points where classified as clean.
        :rtype: `np.ndarray`
        """
        self.set_params(**kwargs)

        if not self.clusters_by_class:
            self.cluster_activations()

        analyzer = ClusteringAnalyzer()

        if self.cluster_analysis == 'smaller':
            self.assigned_clean_by_class, self.poisonous_clusters, report \
                = analyzer.analyze_by_size(self.clusters_by_class)
        elif self.cluster_analysis == 'relative-size':
            self.assigned_clean_by_class, self.poisonous_clusters, report \
                = analyzer.analyze_by_relative_size(self.clusters_by_class)
        elif self.cluster_analysis == 'distance':
            self.assigned_clean_by_class, self.poisonous_clusters, report \
                = analyzer.analyze_by_distance(self.clusters_by_class,
                                               separated_activations=self.red_activations_by_class)
        elif self.cluster_analysis == 'silhouette-scores':
            self.assigned_clean_by_class, self.poisonous_clusters, report \
                = analyzer.analyze_by_silhouette_score(self.clusters_by_class,
                                                       reduced_activations_by_class=self.red_activations_by_class)
        else:
            raise ValueError(
                "Unsupported cluster analysis technique " + self.cluster_analysis)

        # Add to the report current parameters used to run the defence and the analysis summary
        report = dict(list(report.items()) + list(self.get_params().items()))

        return report, self.assigned_clean_by_class