def parse_dataset_definition(
    config: Dict[str, Any], load_version: str = None, save_version: str = None
) -> Tuple[Type[AbstractDataSet], Dict[str, Any]]:
    """Parse and instantiate a dataset class using the configuration provided.

    Args:
        config: Data set config dictionary. It *must* contain the `type` key
            with fully qualified class name.
        load_version: Version string to be used for ``load`` operation if
                the data set is versioned. Has no effect on the data set
                if versioning was not enabled.
        save_version: Version string to be used for ``save`` operation if
            the data set is versioned. Has no effect on the data set
            if versioning was not enabled.

    Raises:
        DataSetError: If the function fails to parse the configuration provided.

    Returns:
        2-tuple: (Dataset class object, configuration dictionary)
    """
    save_version = save_version or generate_timestamp()
    config = copy.deepcopy(config)

    if "type" not in config:
        raise DataSetError("`type` is missing from DataSet catalog configuration")

    class_obj = config.pop("type")

    if isinstance(class_obj, str):
        try:
            class_obj = load_obj(class_obj, "kedro.io")
        except ImportError:
            raise DataSetError(
                "Cannot import module when trying to load type `{}`.".format(class_obj)
            )
        except AttributeError:
            raise DataSetError("Class `{}` not found.".format(class_obj))

    if not issubclass(class_obj, AbstractDataSet):
        raise DataSetError(
            "DataSet type `{}.{}` is invalid: all data set types must extend "
            "`AbstractDataSet`.".format(class_obj.__module__, class_obj.__qualname__)
        )

    if VERSION_KEY in config:
        # remove "version" key so that it's not passed
        # to the "unversioned" data set constructor
        message = (
            "`%s` attribute removed from data set configuration since it is a "
            "reserved word and cannot be directly specified"
        )
        logging.getLogger(__name__).warning(message, VERSION_KEY)
        del config[VERSION_KEY]
    if config.pop(VERSIONED_FLAG_KEY, False):  # data set is versioned
        config[VERSION_KEY] = Version(load_version, save_version)

    return class_obj, config