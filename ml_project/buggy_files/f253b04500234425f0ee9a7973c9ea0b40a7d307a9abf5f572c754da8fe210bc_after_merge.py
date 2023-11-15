    def cluster_vectorspace(self, vectors, trace=False):
        if self._means and self._repeats > 1:
            print('Warning: means will be discarded for subsequent trials')

        meanss = []
        for trial in range(self._repeats):
            if trace: print('k-means trial', trial)
            if not self._means or trial > 1:
                self._means = self._rng.sample(list(vectors), self._num_means)
            self._cluster_vectorspace(vectors, trace)
            meanss.append(self._means)

        if len(meanss) > 1:
            # sort the means first (so that different cluster numbering won't
            # effect the distance comparison)
            for means in meanss:
                means.sort(key=sum)

            # find the set of means that's minimally different from the others
            min_difference = min_means = None
            for i in range(len(meanss)):
                d = 0
                for j in range(len(meanss)):
                    if i != j:
                        d += self._sum_distances(meanss[i], meanss[j])
                if min_difference is None or d < min_difference:
                    min_difference, min_means = d, meanss[i]

            # use the best means
            self._means = min_means