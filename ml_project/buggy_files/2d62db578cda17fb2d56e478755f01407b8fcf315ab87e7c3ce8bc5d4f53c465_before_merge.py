def deserialize(collection, topological=True):
    """
    Load a collection from file system.

    :param collection: The collection type the deserialize
    :param topological: If the dict/list should be sorted or not.
    :type topological: bool
    """

    datastruct = deserialize_raw(collection.collection_types())
    if topological and type(datastruct) == list:
        # FIXME
        # datastruct.sort(key=__depth_cmp)
        pass
    if type(datastruct) == dict:
        collection.from_dict(datastruct)
    elif type(datastruct) == list:
        collection.from_list(datastruct)