def deserialize(collection, topological=True):
    """
    Load a collection from disk.

    :param collection: The Cobbler collection to know the type of the item.
    :param topological: Unkown parameter.
    :type topological: bool
    """
    __grab_lock()
    storage_module = __get_storage_module(collection.collection_type())
    storage_module.deserialize(collection, topological)
    __release_lock()