def perform_codegen():
    # Set root codegen output directory
    # ---------------------------------
    # (relative to project root)
    outdir = 'plotly'

    # Delete prior codegen output
    # ---------------------------
    validators_pkgdir = opath.join(outdir, 'validators')
    if opath.exists(validators_pkgdir):
        shutil.rmtree(validators_pkgdir)

    graph_objs_pkgdir = opath.join(outdir, 'graph_objs')
    if opath.exists(graph_objs_pkgdir):
        shutil.rmtree(graph_objs_pkgdir)

    # plotly/datatypes is not used anymore, but was at one point so we'll
    # still delete it if we find it in case a developer is upgrading from an
    # older version
    datatypes_pkgdir = opath.join(outdir, 'datatypes')
    if opath.exists(datatypes_pkgdir):
        shutil.rmtree(datatypes_pkgdir)

    # Load plotly schema
    # ------------------
    with open('plotly/package_data/plot-schema.json', 'r') as f:
        plotly_schema = json.load(f)

    # Preprocess Schema
    # -----------------
    preprocess_schema(plotly_schema)

    # Build node lists
    # ----------------
    # ### TraceNode ###
    base_traces_node = TraceNode(plotly_schema)
    compound_trace_nodes = PlotlyNode.get_all_compound_datatype_nodes(
        plotly_schema, TraceNode)
    all_trace_nodes = PlotlyNode.get_all_datatype_nodes(
        plotly_schema, TraceNode)

    # ### LayoutNode ###
    compound_layout_nodes = PlotlyNode.get_all_compound_datatype_nodes(
        plotly_schema, LayoutNode)
    layout_node = compound_layout_nodes[0]
    all_layout_nodes = PlotlyNode.get_all_datatype_nodes(
        plotly_schema, LayoutNode)

    # ### FrameNode ###
    compound_frame_nodes = PlotlyNode.get_all_compound_datatype_nodes(
        plotly_schema, FrameNode)
    frame_node = compound_frame_nodes[0]
    all_frame_nodes = PlotlyNode.get_all_datatype_nodes(
        plotly_schema, FrameNode)

    # ### All nodes ###
    all_datatype_nodes = (all_trace_nodes +
                          all_layout_nodes +
                          all_frame_nodes)

    all_compound_nodes = [node for node in all_datatype_nodes
                          if node.is_compound and
                          not isinstance(node, ElementDefaultsNode)]

    # Write out validators
    # --------------------
    # # ### Layout ###
    for node in all_layout_nodes:
        write_validator_py(outdir, node)

    # ### Trace ###
    for node in all_trace_nodes:
        write_validator_py(outdir, node)

    # ### Frames ###
    for node in all_frame_nodes:
        write_validator_py(outdir, node)

    # ### Data (traces) validator ###
    write_data_validator_py(outdir, base_traces_node)

    # Write out datatypes
    # -------------------
    # ### Layout ###
    for node in compound_layout_nodes:
        write_datatype_py(outdir, node)

    # ### Trace ###
    for node in compound_trace_nodes:
        write_datatype_py(outdir, node)

    # ### Frames ###
    for node in compound_frame_nodes:
        write_datatype_py(outdir, node)

    # ### Deprecated ###
    # These are deprecated legacy datatypes like graph_objs.Marker
    write_deprecated_datatypes(outdir)

    # Write figure class to graph_objs
    # --------------------------------
    data_validator = get_data_validator_instance(base_traces_node)
    layout_validator = layout_node.get_validator_instance()
    frame_validator = frame_node.get_validator_instance()

    write_figure_classes(outdir,
                         base_traces_node,
                         data_validator,
                         layout_validator,
                         frame_validator)

    # Write validator __init__.py files
    # ---------------------------------
    # ### Write __init__.py files for each validator package ###
    path_to_validator_import_info = {}
    for node in all_datatype_nodes:
        if node.is_mapped:
            continue
        key = node.parent_path_parts
        path_to_validator_import_info.setdefault(key, []).append(
            (f"._{node.name_property}", node.name_validator_class)
        )

    # Add Data validator
    root_validator_pairs = path_to_validator_import_info[()]
    root_validator_pairs.append(('._data', 'DataValidator'))

    # Output validator __init__.py files
    validators_pkg = opath.join(outdir, 'validators')
    for path_parts, import_pairs in path_to_validator_import_info.items():
        write_init_py(validators_pkg, path_parts, import_pairs)

    # Write datatype __init__.py files
    # --------------------------------
    # ### Build mapping from parent package to datatype class ###
    path_to_datatype_import_info = {}
    for node in all_compound_nodes:
        key = node.parent_path_parts

        # class import
        path_to_datatype_import_info.setdefault(key, []).append(
            (f"._{node.name_undercase}", node.name_datatype_class)
        )

        # submodule import
        if node.child_compound_datatypes:
            
            path_to_datatype_import_info.setdefault(key, []).append(
                (f"plotly.graph_objs{node.parent_dotpath_str}",
                 node.name_undercase)
            )

    # ### Write plotly/graph_objs/graph_objs.py ###
    # This if for backward compatibility. It just imports everything from
    # graph_objs/__init__.py
    write_graph_objs_graph_objs(outdir)

    # ### Add Figure and FigureWidget ###
    root_datatype_imports = path_to_datatype_import_info[()]
    root_datatype_imports.append(('._figure', 'Figure'))

    optional_figure_widget_import = """
try:
    import ipywidgets
    from distutils.version import LooseVersion
    if LooseVersion(ipywidgets.__version__) >= LooseVersion('7.0.0'):
        from ._figurewidget import FigureWidget
    del LooseVersion
    del ipywidgets
except ImportError:
    pass
"""
    root_datatype_imports.append(optional_figure_widget_import)

    # ### Add deprecations ###
    root_datatype_imports.append(('._deprecations', DEPRECATED_DATATYPES.keys()))

    # ### Output datatype __init__.py files ###
    graph_objs_pkg = opath.join(outdir, 'graph_objs')
    for path_parts, import_pairs in path_to_datatype_import_info.items():
        write_init_py(graph_objs_pkg, path_parts, import_pairs)