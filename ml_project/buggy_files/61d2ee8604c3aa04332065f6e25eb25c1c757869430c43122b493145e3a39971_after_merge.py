def add_collection_plugins(plugin_list, plugin_type, coll_filter=None):

    # TODO: take into account routing.yml once implemented
    b_colldirs = list_collection_dirs(coll_filter=coll_filter)
    for b_path in b_colldirs:
        path = to_text(b_path, errors='surrogate_or_strict')
        collname = get_collection_name_from_path(b_path)
        ptype = C.COLLECTION_PTYPE_COMPAT.get(plugin_type, plugin_type)
        plugin_list.update(DocCLI.find_plugins(os.path.join(path, 'plugins', ptype), plugin_type, collection=collname))