    def get_tags_for_cluster(self, cluster_mid=None):
        """
        Return list of tag object associated with cluster
        Args:
            cluster_mid: Dynamic object for cluster

        Returns: List of tag object associated with the given cluster

        """
        return self.get_tags_for_dynamic_obj(mid=cluster_mid)