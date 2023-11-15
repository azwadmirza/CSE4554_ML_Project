    def analyze_by_relative_size(self, separated_clusters, size_threshold=0.35):
        """
        Assigns a cluster as poisonous if the smaller one contains less than threshold of the data.
        This method assumes only 2 clusters

        :param separated_clusters: list where separated_clusters[i] is the cluster assignments for the ith class
        :type separated_clusters: `list`
        :param size_threshold: (optional) threshold used to define when a cluster is substantially smaller. A default
        value is used if the parameter is not provided.
        :type size_threshold: `float`
        :return: all_assigned_clean, summary_poison_clusters:
        where all_assigned_clean[i] is a 1D boolean array indicating whether
        a given data point was determined to be clean (as opposed to poisonous) and
        summary_poison_clusters: array, where  summary_poison_clusters[i][j]=1 if cluster j of class i was classified as
        poison, otherwise 0
        :rtype: all_assigned_clean: `ndarray`, summary_poison_clusters: `list`
        """
        all_assigned_clean = []
        nb_classes = len(separated_clusters)
        nb_clusters = len(np.unique(separated_clusters[0]))
        summary_poison_clusters = [[[] for x in range(nb_clusters)] for y in range(nb_classes)]

        for i, clusters in enumerate(separated_clusters):
            bins = np.bincount(clusters)
            if np.size(bins) > 2:
                raise ValueError(" RelativeSizeAnalyzer does not support more than two clusters.")
            percentages = bins / float(np.sum(bins))
            poison_clusters = np.where(percentages < size_threshold)
            clean_clusters = np.where(percentages >= size_threshold)

            for p_id in poison_clusters[0]:
                summary_poison_clusters[i][p_id] = 1
            for c_id in clean_clusters[0]:
                summary_poison_clusters[i][c_id] = 0

            assigned_clean = self.assign_class(clusters, clean_clusters, poison_clusters)
            all_assigned_clean.append(assigned_clean)

        return np.asarray(all_assigned_clean), summary_poison_clusters