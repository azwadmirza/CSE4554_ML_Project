async def remove_instance(
    instance,
    interactive: bool = False,
    drop_db: Optional[bool] = None,
    remove_datapath: Optional[bool] = None,
):
    data_manager.load_basic_configuration(instance)

    if confirm("Would you like to make a backup of the data for this instance? (y/n)"):
        await create_backup(instance)

    backend = get_current_backend(instance)
    if backend == BackendType.MONGOV1:
        driver_cls = drivers.MongoDriver
    else:
        driver_cls = drivers.get_driver_class(backend)

    await driver_cls.delete_all_data(interactive=interactive, drop_db=drop_db)

    if interactive is True and remove_datapath is None:
        remove_datapath = confirm("Would you like to delete the instance's entire datapath? (y/n)")

    if remove_datapath is True:
        data_path = data_manager.core_data_path().parent
        safe_delete(data_path)

    save_config(instance, {}, remove=True)
    print("The instance {} has been removed\n".format(instance))