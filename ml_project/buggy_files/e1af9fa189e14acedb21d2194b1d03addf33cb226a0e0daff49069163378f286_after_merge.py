def deserialize(collection, topological=True):
    """
    Load a collection from the database.

    :param collection: The collection to deserialize.
    :param topological: If the collection list should be sorted by the
                        collection dict depth value or not.
    :type topological: bool
    """

    datastruct = deserialize_raw(collection.collection_type())
    if topological and type(datastruct) == list:
        datastruct.sort(key = lambda x: x["depth"])
    if type(datastruct) == dict:
        collection.from_dict(datastruct)
    elif type(datastruct) == list:
        collection.from_list(datastruct)