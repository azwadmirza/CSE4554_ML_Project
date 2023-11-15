async def remove_instance(selected, instance_data):
    if instance_data["STORAGE_TYPE"] == "MongoDB":
        from redbot.core.drivers.red_mongo import Mongo

        m = Mongo("Core", **instance_data["STORAGE_DETAILS"])
        db = m.db
        collections = await db.collection_names(include_system_collections=False)
        for name in collections:
            collection = await db.get_collection(name)
            await collection.drop()
    else:
        pth = Path(instance_data["DATA_PATH"])
        safe_delete(pth)
    save_config(selected, {}, remove=True)
    print("The instance {} has been removed\n".format(selected))