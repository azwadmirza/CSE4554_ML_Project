def get_driver(
    cog_name: str,
    identifier: str,
    storage_type: Optional[BackendType] = None,
    *,
    allow_old: bool = False,
    **kwargs,
):
    """Get a driver instance.

    Parameters
    ----------
    cog_name : str
        The cog's name.
    identifier : str
        The cog's discriminator.
    storage_type : Optional[BackendType]
        The backend you want a driver for. Omit to try to obtain the
        backend from data manager.
    **kwargs
        Driver-specific keyword arguments.

    Returns
    -------
    BaseDriver
        A driver instance.

    Raises
    ------
    RuntimeError
        If the storage type is MongoV1, Mongo, or invalid.

    """
    if storage_type is None:
        try:
            storage_type = BackendType(data_manager.storage_type())
        except RuntimeError:
            storage_type = BackendType.JSON

    try:
        if not allow_old:
            driver_cls: Type[BaseDriver] = get_driver_class(storage_type)
        else:
            driver_cls: Type[BaseDriver] = _get_driver_class_include_old(storage_type)
    except ValueError:
        if storage_type in (BackendType.MONGOV1, BackendType.MONGO):
            raise RuntimeError(
                "Please convert to JSON first to continue using the bot."
                "Mongo support was removed in 3.2."
            ) from None
        else:
            raise RuntimeError(f"Invalid driver type: '{storage_type}'") from None
    return driver_cls(cog_name, identifier, **kwargs)