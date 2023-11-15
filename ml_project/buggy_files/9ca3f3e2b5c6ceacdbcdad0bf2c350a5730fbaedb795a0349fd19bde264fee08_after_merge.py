    def analyze_by_distance(self, separated_clusters, separated_activations):
        """
        Assigns a cluster as poisonous if its median activation is closer to the median activation for another class
        than it is to the median activation of its own class. Currently, this function assumes there are only
        two clusters per class.

        :param separated_clusters: list where separated_clusters[i] is the cluster assignments for the ith class
        :type separated_clusters: `list`
        :param separated_activations: list where separated_activations[i] is a 1D array of [0,1] for [poison,clean]
        :type separated_clusters: `list`
        :return: all_assigned_clean, summary_poison_clusters, report:
        where all_assigned_clean[i] is a 1D boolean array indicating whether
        a given data point was determined to be clean (as opposed to poisonous) and
        summary_poison_clusters: array, where  summary_poison_clusters[i][j]=1 if cluster j of class i was classified as
        poison, otherwise 0
        report: Dictionary with summary of the analysis
        :rtype: all_assigned_clean: `ndarray`, summary_poison_clusters: `list`, report" `dic`
        """
        report = {'cluster_analysis': 'distance'
                  }

        all_assigned_clean = []
        cluster_centers = []

        nb_classes = len(separated_clusters)
        nb_clusters = len(np.unique(separated_clusters[0]))
        summary_poison_clusters = [[[] for x in range(nb_clusters)] for y in range(nb_classes)]

        # assign centers
        for t, activations in enumerate(separated_activations):
            cluster_centers.append(np.median(activations, axis=0))

        for i, (clusters, ac) in enumerate(zip(separated_clusters, separated_activations)):
            clusters = np.array(clusters)

            cluster0_center = np.median(ac[np.where(clusters == 0)], axis=0)
            cluster1_center = np.median(ac[np.where(clusters == 1)], axis=0)

            cluster0_distance = np.linalg.norm(cluster0_center - cluster_centers[i])
            cluster1_distance = np.linalg.norm(cluster1_center - cluster_centers[i])

            cluster0_is_poison = False
            cluster1_is_poison = False

            dict_k = dict()
            dict_cluster_0 = dict(cluster0_distance_to_its_class=cluster0_distance)
            dict_cluster_1 = dict(cluster1_distance_to_its_class=cluster1_distance)
            for k, center in enumerate(cluster_centers):
                if k == i:
                    pass
                else:
                    cluster0_distance_to_k = np.linalg.norm(cluster0_center - center)
                    cluster1_distance_to_k = np.linalg.norm(cluster1_center - center)

                    if cluster0_distance_to_k < cluster0_distance and cluster1_distance_to_k > cluster1_distance:
                        cluster0_is_poison = True
                    if cluster1_distance_to_k < cluster1_distance and cluster0_distance_to_k > cluster0_distance:
                        cluster1_is_poison = True

                    dict_cluster_0['distance_to_class_'+str(k)] = cluster0_distance_to_k
                    dict_cluster_0['suspicious'] = cluster0_is_poison

                    dict_cluster_1['distance_to_class_'+str(k)] = cluster1_distance_to_k
                    dict_cluster_1['suspicious'] = cluster1_is_poison

                    dict_k.update(dict_cluster_0)
                    dict_k.update(dict_cluster_1)

            report_class = dict(cluster_0=dict_cluster_0, cluster_1=dict_cluster_1)
            report['Class_' + str(i)] = report_class

            poison_clusters = []
            if cluster0_is_poison:
                poison_clusters.append(0)
                summary_poison_clusters[i][0] = 1
            else:
                summary_poison_clusters[i][0] = 0

            if cluster1_is_poison:
                poison_clusters.append(1)
                summary_poison_clusters[i][1] = 1
            else:
                summary_poison_clusters[i][1] = 0

            clean_clusters = list(set(clusters) - set(poison_clusters))
            assigned_clean = self.assign_class(clusters, clean_clusters, poison_clusters)
            all_assigned_clean.append(assigned_clean)

        all_assigned_clean = np.asarray(all_assigned_clean)
        return all_assigned_clean, summary_poison_clusters, report