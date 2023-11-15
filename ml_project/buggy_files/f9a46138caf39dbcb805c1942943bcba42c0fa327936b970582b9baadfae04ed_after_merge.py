async def json_to_mongo(current_data_dir: Path, storage_details: dict):
    from redbot.core.drivers.red_mongo import Mongo

    core_data_file = current_data_dir / "core" / "settings.json"
    driver = Mongo(cog_name="Core", identifier="0", **storage_details)
    with core_data_file.open(mode="r") as f:
        core_data = json.loads(f.read())
    data = core_data.get("0", {})
    for key, value in data.items():
        await driver.set(key, value=value)
    for p in current_data_dir.glob("cogs/**/settings.json"):
        cog_name = p.parent.stem
        with p.open(mode="r") as f:
            cog_data = json.load(f)
        for identifier, data in cog_data.items():
            driver = Mongo(cog_name, identifier, **storage_details)
            for key, value in data.items():
                await driver.set(key, value=value)