async def mongo_to_json(current_data_dir: Path, storage_details: dict):
    from redbot.core.drivers.red_mongo import Mongo

    m = Mongo("Core", "0", **storage_details)
    db = m.db
    collection_names = await db.collection_names(include_system_collections=False)
    for c_name in collection_names:
        if c_name == "Core":
            c_data_path = current_data_dir / "core"
        else:
            c_data_path = current_data_dir / "cogs/{}".format(c_name)
        output = {}
        docs = await db[c_name].find().to_list(None)
        c_id = None
        for item in docs:
            item_id = item.pop("_id")
            if not c_id:
                c_id = str(hash(item_id))
            output[item_id] = item
        target = JSON(c_name, c_id, data_path_override=c_data_path)
        await target.jsonIO._threadsafe_save_json(output)