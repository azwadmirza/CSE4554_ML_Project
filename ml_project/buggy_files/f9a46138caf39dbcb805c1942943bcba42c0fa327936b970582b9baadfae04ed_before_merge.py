async def json_to_mongo(current_data_dir: Path, storage_details: dict):
    from redbot.core.drivers.red_mongo import Mongo

    core_data_file = list(current_data_dir.glob("core/settings.json"))[0]
    m = Mongo("Core", "0", **storage_details)
    with core_data_file.open(mode="r") as f:
        core_data = json.loads(f.read())
    collection = m.get_collection()
    await collection.update_one(
        {"_id": m.unique_cog_identifier}, update={"$set": core_data["0"]}, upsert=True
    )
    for p in current_data_dir.glob("cogs/**/settings.json"):
        with p.open(mode="r") as f:
            cog_data = json.loads(f.read())
        cog_i = None
        for ident in list(cog_data.keys()):
            cog_i = str(hash(ident))
        cog_m = Mongo(p.parent.stem, cog_i, **storage_details)
        cog_c = cog_m.get_collection()
        for ident in list(cog_data.keys()):
            await cog_c.update_one(
                {"_id": cog_m.unique_cog_identifier}, update={"$set": cog_data[cog_i]}, upsert=True
            )