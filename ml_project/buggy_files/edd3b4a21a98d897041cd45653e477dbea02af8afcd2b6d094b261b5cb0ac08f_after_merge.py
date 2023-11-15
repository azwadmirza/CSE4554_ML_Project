def deserialize(collection, topological=True):
    """
    Load a collection from disk.

    :param collection: The Cobbler collection to know the type of the item.
    :param topological: Sort collection based on each items' depth attribute
                        in the list of collection items.  This ensures
                        properly ordered object loading from disk with
                        objects having parent/child relationships, i.e.
                        profiles/subprofiles.  See cobbler/items/item.py
    :type topological: bool
    """
    __grab_lock()
    storage_module = __get_storage_module(collection.collection_type())
    storage_module.deserialize(collection, topological)
    __release_lock()