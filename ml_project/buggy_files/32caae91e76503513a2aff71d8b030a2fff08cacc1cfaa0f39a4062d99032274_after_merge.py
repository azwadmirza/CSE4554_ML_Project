def save_as_osm(
        data, node_tags=settings.osm_xml_node_tags,
        node_attrs=settings.osm_xml_node_attrs,
        edge_tags=settings.osm_xml_way_tags,
        edge_attrs=settings.osm_xml_way_attrs,
        oneway=False, merge_edges=True, edge_tag_aggs=None,
        filename='graph.osm', folder=None):
    """
    Save a graph as an OSM XML formatted file. NOTE: for very large
    networks this method can take upwards of 30+ minutes to finish.

    Parameters
    __________
    data : networkx multi(di)graph OR a length 2 iterable of nodes/edges
        geopandas.GeoDataFrames
    filename : string
        the name of the osm file (including file extension)
    folder : string
        the folder to contain the file, if None, use default data folder
    node_attrs: list
        osm node attributes to include in output OSM XML
    edge_tags : list
        osm way tags to include in output OSM XML
    edge_attrs : list
        osm way attributes to include in output OSM XML
    oneway : bool
        the default oneway value used to fill this tag where missing
    merge_edges : bool
        if True merges graph edges such that each OSM way has one entry
            and one entry only in the OSM XML. Otherwise, every OSM way
            will have a separate entry for each node pair it contains.
    edge_tag_aggs : list of length-2 string tuples
        useful only if merge_edges is True, this argument allows the user
            to specify edge attributes to aggregate such that the merged
            OSM way entry tags accurately represent the sum total of
            their component edge attributes. For example, if the user
            wants the OSM way to have a "length" attribute, the user must
            specify `edge_tag_aggs=[('length', 'sum')]` in order to tell
            this method to aggregate the lengths of the individual
            component edges. Otherwise, the length attribute will simply
            reflect the length of the first edge associated with the way.

    Returns
    -------
    None
    """
    start_time = time.time()
    if folder is None:
        folder = settings.data_folder

    try:
        assert settings.all_oneway
    except AssertionError:
        raise UserWarning(
            "In order for ox.save_as_osm() to behave properly "
            "the graph must have been created with the 'all_oneway' "
            "setting set to True.")

    try:
        gdf_nodes, gdf_edges = data
    except ValueError:
        gdf_nodes, gdf_edges = graph_to_gdfs(
            data, node_geometry=False, fill_edge_geometry=False)

    # rename columns per osm specification
    gdf_nodes.rename(
        columns={'osmid': 'id', 'x': 'lon', 'y': 'lat'}, inplace=True)
    if 'id' in gdf_edges.columns:
        gdf_edges = gdf_edges[[col for col in gdf_edges if col != 'id']]
    if 'uniqueid' in gdf_edges.columns:
        gdf_edges = gdf_edges.rename(columns={'uniqueid': 'id'})
    else:
        gdf_edges = gdf_edges.reset_index().rename(columns={'index': 'id'})

    # add default values for required attributes
    for table in [gdf_nodes, gdf_edges]:
        table['uid'] = '1'
        table['user'] = 'osmnx'
        table['version'] = '1'
        table['changeset'] = '1'
        table['timestamp'] = '2017-01-01T00:00:00Z'

    # convert all datatypes to str
    nodes = gdf_nodes.applymap(str)
    edges = gdf_edges.applymap(str)

    # misc. string replacements to meet OSM XML spec
    if 'oneway' in edges.columns:

        # fill blank oneway tags with default (False)
        edges.loc[pd.isnull(edges['oneway']), 'oneway'] = oneway
        edges.loc[:, 'oneway'] = edges['oneway'].astype(str)
        edges.loc[:, 'oneway'] = edges['oneway'].str.replace(
            'False', 'no').replace('True', 'yes')

    # initialize XML tree with an OSM root element
    root = etree.Element('osm', attrib={'version': '1', 'generator': 'OSMnx'})

    # append nodes to the XML tree
    for i, row in nodes.iterrows():
        node = etree.SubElement(
            root, 'node', attrib=row[node_attrs].dropna().to_dict())
        for tag in node_tags:
            if tag in nodes.columns:
                etree.SubElement(
                    node, 'tag', attrib={'k': tag, 'v': row[tag]})

    # append edges to the XML tree
    if merge_edges:
        for e in edges['id'].unique():
            all_way_edges = edges[edges['id'] == e]
            first = all_way_edges.iloc[0]
            edge = etree.SubElement(
                root, 'way', attrib=first[edge_attrs].dropna().to_dict())

            if len(all_way_edges) == 1:

                etree.SubElement(edge, 'nd', attrib={'ref': first['u']})
                etree.SubElement(edge, 'nd', attrib={'ref': first['v']})

            else:

                # topological sort
                ordered_nodes = get_unique_nodes_ordered_from_way(
                    all_way_edges)

                for node in ordered_nodes:
                    etree.SubElement(edge, 'nd', attrib={'ref': node})

            if edge_tag_aggs is None:
                for tag in edge_tags:
                    if tag in all_way_edges.columns:
                        etree.SubElement(
                            edge, 'tag', attrib={'k': tag, 'v': first[tag]})
            else:
                for tag in edge_tags:
                    if tag in all_way_edges.columns:
                        if tag not in [t for t, agg in edge_tag_aggs]:
                            etree.SubElement(
                                edge, 'tag',
                                attrib={'k': tag, 'v': first[tag]})

                for tag, agg in edge_tag_aggs:
                    if tag in all_way_edges.columns:
                        etree.SubElement(edge, 'tag', attrib={
                            'k': tag, 'v': all_way_edges[tag].aggregate(agg)})

    else:

        # NOTE: this will generate separate OSM ways for each network edge,
        # even if the edges are all part of the same original OSM way. As
        # such, each way will be comprised of two nodes, and there will be
        # many ways with the same OSM id. This does not conform to the
        # OSM XML schema standard, however, the data will still comprise a
        # valid network and will be readable by *most* OSM tools.
        for i, row in edges.iterrows():
            edge = etree.SubElement(
                root, 'way', attrib=row[edge_attrs].dropna().to_dict())
            etree.SubElement(edge, 'nd', attrib={'ref': row['u']})
            etree.SubElement(edge, 'nd', attrib={'ref': row['v']})
            for tag in edge_tags:
                if tag in edges.columns:
                    etree.SubElement(
                        edge, 'tag', attrib={'k': tag, 'v': row[tag]})

    et = etree.ElementTree(root)

    if not os.path.exists(folder):
        os.makedirs(folder)

    et.write(os.path.join(folder, filename))

    log('Saved graph to disk as OSM at "{}" in {:,.2f} seconds'.format(
        os.path.join(folder, filename), time.time() - start_time))