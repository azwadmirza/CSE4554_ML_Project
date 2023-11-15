def deserialize(collection, topological=True):
    """
    Load a collection from the database.

    :param collection: The collection to deserialize.
    :param topological: This sorts the returned dict.
    :type topological: bool
    """

    datastruct = deserialize_raw(collection.collection_type())
    if topological and type(datastruct) == list:
        datastruct.sort(__depth_cmp)
    if type(datastruct) == dict:
        collection.from_dict(datastruct)
    elif type(datastruct) == list:
        collection.from_list(datastruct)