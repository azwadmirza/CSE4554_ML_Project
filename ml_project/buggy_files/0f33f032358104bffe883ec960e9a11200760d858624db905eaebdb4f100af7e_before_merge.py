    def _calc_vertices_regions(self):
        """
        Calculates the Voronoi vertices and regions of the generators stored
        in self.points. The vertices will be stored in self.vertices and the
        regions in self.regions.

        This algorithm was discussed at PyData London 2015 by
        Tyler Reddy, Ross Hemsley and Nikolai Nowaczyk
        """

        # perform 3D Delaunay triangulation on data set
        # (here ConvexHull can also be used, and is faster)
        self._tri = scipy.spatial.ConvexHull(self.points)

        # add the center to each of the simplices in tri to get the same
        # tetrahedrons we'd have gotten from Delaunay tetrahedralization
        tetrahedrons = self._tri.points[self._tri.simplices]
        tetrahedrons = np.insert(
            tetrahedrons,
            3,
            np.array([self.center]),
            axis=1
        )

        # produce circumcenters of tetrahedrons from 3D Delaunay
        circumcenters = calc_circumcenters(tetrahedrons)

        # project tetrahedron circumcenters to the surface of the sphere
        self.vertices = project_to_sphere(
            circumcenters,
            self.center,
            self.radius
        )

        # calculate regions from triangulation
        generator_indices = np.arange(self.points.shape[0])
        filter_tuple = np.where((np.expand_dims(self._tri.simplices,
                                -1) == generator_indices).any(axis=1))

        list_tuples_associations = zip(filter_tuple[1],
                                       filter_tuple[0])

        list_tuples_associations = sorted(list_tuples_associations,
                                          key=lambda t: t[0])

        # group by generator indices to produce
        # unsorted regions in nested list
        groups = []
        for k, g in itertools.groupby(list_tuples_associations,
                                      lambda t: t[0]):
            groups.append([element[1] for element in list(g)])

        self.regions = groups