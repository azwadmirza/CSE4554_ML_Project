async def migrate(cur_driver_cls: Type[BaseDriver], new_driver_cls: Type[BaseDriver]) -> None:
    """Migrate from one driver type to another."""
    # Get custom group data
    core_conf = Config.get_core_conf()
    core_conf.init_custom("CUSTOM_GROUPS", 2)
    all_custom_group_data = await core_conf.custom("CUSTOM_GROUPS").all()

    await cur_driver_cls.migrate_to(new_driver_cls, all_custom_group_data)