def delete(
    instance: str,
    interactive: bool,
    _create_backup: Optional[bool],
    drop_db: Optional[bool],
    remove_datapath: Optional[bool],
):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        remove_instance(instance, interactive, _create_backup, drop_db, remove_datapath)
    )