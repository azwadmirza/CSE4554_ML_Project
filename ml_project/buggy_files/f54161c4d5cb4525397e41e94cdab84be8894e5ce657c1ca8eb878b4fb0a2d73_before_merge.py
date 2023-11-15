def truncate_graph_polygon(G, polygon, retain_all=False, truncate_by_edge=False, quadrat_width=0.05, min_num=3, buffer_amount=1e-9):
    """
    Remove every node in graph that falls outside some shapely Polygon or
    MultiPolygon.

    Parameters
    ----------
    G : networkx multidigraph
    polygon : Polygon or MultiPolygon
        only retain nodes in graph that lie within this geometry
    retain_all : bool
        if True, return the entire graph even if it is not connected
    truncate_by_edge : bool
        if True retain node if it's outside polygon but at least one of node's
        neighbors are within polygon (NOT CURRENTLY IMPLEMENTED)
    quadrat_width : numeric
        passed on to intersect_index_quadrats: the linear length (in degrees) of
        the quadrats with which to cut up the geometry (default = 0.05, approx
        4km at NYC's latitude)
    min_num : int
        passed on to intersect_index_quadrats: the minimum number of linear
        quadrat lines (e.g., min_num=3 would produce a quadrat grid of 4
        squares)
    buffer_amount : numeric
        passed on to intersect_index_quadrats: buffer the quadrat grid lines by
        quadrat_width times buffer_amount

    Returns
    -------
    networkx multidigraph
    """

    start_time = time.time()
    G = G.copy()
    log('Identifying all nodes that lie outside the polygon...')

    # get a GeoDataFrame of all the nodes, for spatial analysis
    node_geom = [Point(data['x'], data['y']) for _, data in G.nodes(data=True)]
    gdf_nodes = gpd.GeoDataFrame({'node':pd.Series(G.nodes()), 'geometry':node_geom})
    gdf_nodes.crs = G.graph['crs']

    # find all the nodes in the graph that lie outside the polygon
    points_within_geometry = intersect_index_quadrats(gdf_nodes, polygon, quadrat_width=quadrat_width, min_num=min_num, buffer_amount=buffer_amount)
    nodes_outside_polygon = gdf_nodes[~gdf_nodes.index.isin(points_within_geometry.index)]

    # now remove from the graph all those nodes that lie outside the place
    # polygon
    start_time = time.time()
    G.remove_nodes_from(nodes_outside_polygon['node'])
    log('Removed {:,} nodes outside polygon in {:,.2f} seconds'.format(len(nodes_outside_polygon), time.time()-start_time))

    # remove any isolated nodes and retain only the largest component (if retain_all is False)
    if not retain_all:
        G = remove_isolated_nodes(G)
        G = get_largest_component(G)

    return G