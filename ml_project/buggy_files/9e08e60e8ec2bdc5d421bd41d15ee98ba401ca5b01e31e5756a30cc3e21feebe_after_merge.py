async def remove_instance(
    instance,
    interactive: bool = False,
    delete_data: Optional[bool] = None,
    _create_backup: Optional[bool] = None,
    drop_db: Optional[bool] = None,
    remove_datapath: Optional[bool] = None,
):
    data_manager.load_basic_configuration(instance)

    if interactive is True and delete_data is None:
        delete_data = click.confirm(
            "Would you like to delete this instance's data?", default=False
        )

    if interactive is True and _create_backup is None:
        _create_backup = click.confirm(
            "Would you like to make a backup of the data for this instance?", default=False
        )

    if _create_backup is True:
        await create_backup(instance)

    backend = get_current_backend(instance)
    driver_cls = drivers.get_driver_class(backend)
    await driver_cls.initialize(**data_manager.storage_details())
    try:
        if delete_data is True:
            await driver_cls.delete_all_data(interactive=interactive, drop_db=drop_db)

        if interactive is True and remove_datapath is None:
            remove_datapath = click.confirm(
                "Would you like to delete the instance's entire datapath?", default=False
            )

        if remove_datapath is True:
            data_path = data_manager.core_data_path().parent
            safe_delete(data_path)

        save_config(instance, {}, remove=True)
    finally:
        await driver_cls.teardown()
    print("The instance {} has been removed\n".format(instance))