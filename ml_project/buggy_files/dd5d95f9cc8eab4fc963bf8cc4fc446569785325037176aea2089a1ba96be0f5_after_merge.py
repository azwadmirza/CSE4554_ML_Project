async def mongo_to_json(current_data_dir: Path, storage_details: dict):
    from redbot.core.drivers.red_mongo import Mongo

    m = Mongo("Core", "0", **storage_details)
    db = m.db
    collection_names = await db.list_collection_names()
    for collection_name in collection_names:
        if collection_name == "Core":
            c_data_path = current_data_dir / "core"
        else:
            c_data_path = current_data_dir / "cogs" / collection_name
        c_data_path.mkdir(parents=True, exist_ok=True)
        # Every cog name has its own collection
        collection = db[collection_name]
        async for document in collection.find():
            # Every cog has its own document.
            # This means if two cogs have the same name but different identifiers, they will
            # be two separate documents in the same collection
            cog_id = document.pop("_id")
            driver = JSON(collection_name, cog_id, data_path_override=c_data_path)
            for key, value in document.items():
                await driver.set(key, value=value)