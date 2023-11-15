    def __init__(self, n_clusters=2, *, affinity="euclidean",
                 memory=None,
                 connectivity=None, compute_full_tree='auto',
                 linkage='ward', pooling_func=np.mean,
                 distance_threshold=None):
        super().__init__(
            n_clusters=n_clusters, memory=memory, connectivity=connectivity,
            compute_full_tree=compute_full_tree, linkage=linkage,
            affinity=affinity, distance_threshold=distance_threshold)
        self.pooling_func = pooling_func