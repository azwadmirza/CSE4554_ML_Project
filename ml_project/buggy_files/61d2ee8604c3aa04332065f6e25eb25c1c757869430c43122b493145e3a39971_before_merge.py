def add_collection_plugins(plugin_list, plugin_type, coll_filter=None):

    # TODO: take into account routing.yml once implemented
    colldirs = list_collection_dirs(coll_filter=coll_filter)
    for path in colldirs:
        collname = get_collection_name_from_path(path)
        ptype = C.COLLECTION_PTYPE_COMPAT.get(plugin_type, plugin_type)
        plugin_list.update(DocCLI.find_plugins(os.path.join(path, 'plugins', ptype), plugin_type, collname))