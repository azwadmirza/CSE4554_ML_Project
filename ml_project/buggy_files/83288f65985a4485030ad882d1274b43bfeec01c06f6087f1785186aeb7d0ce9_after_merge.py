    def analyze_by_size(self, separated_clusters):
        """
        Designates as poisonous the cluster with less number of items on it.

        :param separated_clusters: list where separated_clusters[i] is the cluster assignments for the ith class
        :type separated_clusters: `list`
        :return: all_assigned_clean, summary_poison_clusters, report:
        where all_assigned_clean[i] is a 1D boolean array indicating whether
        a given data point was determined to be clean (as opposed to poisonous) and
        summary_poison_clusters: array, where  summary_poison_clusters[i][j]=1 if cluster j of class i was classified as
        poison, otherwise 0
        report: Dictionary with summary of the analysis
        :rtype: all_assigned_clean: `ndarray`, summary_poison_clusters: `list`, report" `dic`
        """
        report = {'cluster_analysis': 'smaller',
                  'suspicious_clusters': 0
                  }

        all_assigned_clean = []
        nb_classes = len(separated_clusters)
        nb_clusters = len(np.unique(separated_clusters[0]))
        summary_poison_clusters = [[[] for x in range(nb_clusters)] for y in range(nb_classes)]

        for i, clusters in enumerate(separated_clusters):

            # assume that smallest cluster is poisonous and all others are clean
            sizes = np.bincount(clusters)
            total_dp_in_class = np.sum(sizes)
            poison_clusters = [np.argmin(sizes)]
            clean_clusters = list(set(clusters) - set(poison_clusters))

            for p_id in poison_clusters:
                summary_poison_clusters[i][p_id] = 1
            for c_id in clean_clusters:
                summary_poison_clusters[i][c_id] = 0

            assigned_clean = self.assign_class(clusters, clean_clusters, poison_clusters)
            all_assigned_clean.append(assigned_clean)

            # Generate report for this class:
            report_class = dict()
            for cluster_id in range(nb_clusters):
                ptc = sizes[cluster_id]/total_dp_in_class
                susp = (cluster_id in poison_clusters)
                dict_i = dict(ptc_data_in_cluster=round(ptc, 2), suspicious_cluster=susp)

                dict_cluster = {'cluster_'+str(cluster_id): dict_i}
                report_class.update(dict_cluster)

            report_class['nb_suspicious_clusters'] = len(poison_clusters)
            report['Class_'+str(i)] = report_class

        report['suspicious_clusters'] = report['suspicious_clusters'] + np.sum(summary_poison_clusters)
        return np.asarray(all_assigned_clean), summary_poison_clusters, report