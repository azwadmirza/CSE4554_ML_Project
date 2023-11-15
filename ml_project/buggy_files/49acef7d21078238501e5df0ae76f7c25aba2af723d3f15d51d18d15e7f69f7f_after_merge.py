    def __init__(self, data, kdims=None, vdims=None, **params):
        if isinstance(data, tuple):
            data = data + (None,)*(3-len(data))
            edges, nodes, edgepaths = data
        else:
            edges, nodes, edgepaths = data, None, None

        super(TriMesh, self).__init__(edges, kdims=kdims, vdims=vdims, **params)
        if nodes is None:
            if len(self) == 0:
                nodes = []
            else:
                raise ValueError("TriMesh expects both simplices and nodes "
                                 "to be supplied.")

        if isinstance(nodes, self._node_type):
            pass
        elif isinstance(nodes, Points):
            # Add index to make it a valid Nodes object
            nodes = self._node_type(Dataset(nodes).add_dimension('index', 2, np.arange(len(nodes))))
        elif not isinstance(nodes, Dataset) or nodes.ndims in [2, 3]:
            try:
                # Try assuming data contains indices (3 columns)
                nodes = self._node_type(nodes)
            except:
                # Try assuming data contains just coordinates (2 columns)
                try:
                    points = Points(nodes)
                    ds = Dataset(points).add_dimension('index', 2, np.arange(len(points)))
                    nodes = self._node_type(ds)
                except:
                    raise ValueError("Nodes argument could not be interpreted, expected "
                                     "data with two or three columns representing the "
                                     "x/y positions and optionally the node indices.")
        if edgepaths is not None and not isinstance(edgepaths, self._edge_type):
            edgepaths = self._edge_type(edgepaths)

        self._nodes = nodes
        self._edgepaths = edgepaths