    def _iter_path_collection(paths, path_transforms, offsets, styles):
        """Build an iterator over the elements of the path collection"""
        N = max(len(paths), len(offsets))

        if len(path_transforms) == 0:
            path_transforms = [np.eye(3)]

        edgecolor = styles['edgecolor']
        if np.size(edgecolor) == 0:
            edgecolor = ['none']
        facecolor = styles['facecolor']
        if np.size(facecolor) == 0:
            facecolor = ['none']

        elements = [paths, path_transforms, offsets,
                    edgecolor, styles['linewidth'], facecolor]

        it = itertools
        return it.islice(py3k.zip(*py3k.map(it.cycle, elements)), N)