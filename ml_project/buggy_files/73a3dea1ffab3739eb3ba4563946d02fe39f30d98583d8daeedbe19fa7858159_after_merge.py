    def add_graph(self, adjacency_matrix, node_coords,
                  node_color='auto', node_size=50,
                  edge_cmap=cm.bwr,
                  edge_vmin=None, edge_vmax=None,
                  edge_threshold=None,
                  edge_kwargs=None, node_kwargs=None, colorbar=False,
                  ):
        """Plot undirected graph on each of the axes

        Parameters
        ----------
        adjacency_matrix: numpy array of shape (n, n)
            represents the edges strengths of the graph. Assumed to be
            a symmetric matrix.
        node_coords: numpy array_like of shape (n, 3)
            3d coordinates of the graph nodes in world space.
        node_color: color or sequence of colors
            color(s) of the nodes.
        node_size: scalar or array_like
            size(s) of the nodes in points^2.
        edge_cmap: colormap
            colormap used for representing the strength of the edges.
        edge_vmin: float, optional, default: None
        edge_vmax: float, optional, default: None
            If not None, either or both of these values will be used to
            as the minimum and maximum values to color edges. If None are
            supplied the maximum absolute value within the given threshold
            will be used as minimum (multiplied by -1) and maximum
            coloring levels.
        edge_threshold: str or number
            If it is a number only the edges with a value greater than
            edge_threshold will be shown.
            If it is a string it must finish with a percent sign,
            e.g. "25.3%", and only the edges with a abs(value) above
            the given percentile will be shown.
        edge_kwargs: dict
            will be passed as kwargs for each edge matlotlib Line2D.
        node_kwargs: dict
            will be passed as kwargs to the plt.scatter call that plots all
            the nodes in one go.

        """
        # set defaults
        if edge_kwargs is None:
            edge_kwargs = {}
        if node_kwargs is None:
            node_kwargs = {}
        if isinstance(node_color, str) and node_color == 'auto':
            nb_nodes = len(node_coords)
            node_color = mpl_cm.Set2(np.linspace(0, 1, nb_nodes))
        node_coords = np.asarray(node_coords)

        # decompress input matrix if sparse
        if sparse.issparse(adjacency_matrix):
            adjacency_matrix = adjacency_matrix.toarray()

        # make the lines below well-behaved
        adjacency_matrix = np.nan_to_num(adjacency_matrix)

        # safety checks
        if 's' in node_kwargs:
            raise ValueError("Please use 'node_size' and not 'node_kwargs' "
                             "to specify node sizes")
        if 'c' in node_kwargs:
            raise ValueError("Please use 'node_color' and not 'node_kwargs' "
                             "to specify node colors")

        adjacency_matrix_shape = adjacency_matrix.shape
        if (len(adjacency_matrix_shape) != 2 or
                adjacency_matrix_shape[0] != adjacency_matrix_shape[1]):
            raise ValueError(
                "'adjacency_matrix' is supposed to have shape (n, n)."
                ' Its shape was {0}'.format(adjacency_matrix_shape))

        node_coords_shape = node_coords.shape
        if len(node_coords_shape) != 2 or node_coords_shape[1] != 3:
            message = (
                "Invalid shape for 'node_coords'. You passed an "
                "'adjacency_matrix' of shape {0} therefore "
                "'node_coords' should be a array with shape ({0[0]}, 3) "
                'while its shape was {1}').format(adjacency_matrix_shape,
                                                  node_coords_shape)

            raise ValueError(message)

        if isinstance(node_color, (list, np.ndarray)) and len(node_color) != 1:
            if len(node_color) != node_coords_shape[0]:
                raise ValueError(
                    "Mismatch between the number of nodes ({0}) "
                    "and and the number of node colors ({1})."
                    .format(node_coords_shape[0], len(node_color)))

        if node_coords_shape[0] != adjacency_matrix_shape[0]:
            raise ValueError(
                "Shape mismatch between 'adjacency_matrix' "
                "and 'node_coords'"
                "'adjacency_matrix' shape is {0}, 'node_coords' shape is {1}"
                .format(adjacency_matrix_shape, node_coords_shape))

        if not np.allclose(adjacency_matrix, adjacency_matrix.T, rtol=1e-3):
            raise ValueError("'adjacency_matrix' should be symmetric")

        # For a masked array, masked values are replaced with zeros
        if hasattr(adjacency_matrix, 'mask'):
            if not (adjacency_matrix.mask == adjacency_matrix.mask.T).all():
                raise ValueError(
                    "'adjacency_matrix' was masked with a non symmetric mask")
            adjacency_matrix = adjacency_matrix.filled(0)

        if edge_threshold is not None:
            # Keep a percentile of edges with the highest absolute
            # values, so only need to look at the covariance
            # coefficients below the diagonal
            lower_diagonal_indices = np.tril_indices_from(adjacency_matrix,
                                                          k=-1)
            lower_diagonal_values = adjacency_matrix[
                lower_diagonal_indices]
            edge_threshold = _utils.param_validation.check_threshold(
                edge_threshold, np.abs(lower_diagonal_values),
                stats.scoreatpercentile, 'edge_threshold')

            adjacency_matrix = adjacency_matrix.copy()
            threshold_mask = np.abs(adjacency_matrix) < edge_threshold
            adjacency_matrix[threshold_mask] = 0

        lower_triangular_adjacency_matrix = np.tril(adjacency_matrix, k=-1)
        non_zero_indices = lower_triangular_adjacency_matrix.nonzero()

        line_coords = [node_coords[list(index)]
                       for index in zip(*non_zero_indices)]

        adjacency_matrix_values = adjacency_matrix[non_zero_indices]
        for ax in self.axes.values():
            ax._add_markers(node_coords, node_color, node_size, **node_kwargs)
            if line_coords:
                ax._add_lines(line_coords, adjacency_matrix_values, edge_cmap,
                              vmin=edge_vmin, vmax=edge_vmax,
                              **edge_kwargs)
            # To obtain the brain left view, we simply invert the x axis
            if ax.direction == 'l' and not (ax.ax.get_xlim()[0] > ax.ax.get_xlim()[1]):
                ax.ax.invert_xaxis()

        if colorbar:
            self._colorbar = colorbar
            self._show_colorbar(ax.cmap, ax.norm, threshold=edge_threshold)

        plt.draw_if_interactive()