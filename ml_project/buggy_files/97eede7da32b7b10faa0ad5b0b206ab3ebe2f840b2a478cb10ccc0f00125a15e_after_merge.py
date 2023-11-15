def _split_credentials(
    credentials: Union[Dict[str, Any], None]
) -> Tuple[Dict[str, Any], Any]:
    credentials = deepcopy(credentials) or {}
    if DATASET_CREDENTIALS_KEY in credentials:
        warn(
            "Support for `{}` key in the credentials is now deprecated and will be "
            "removed in the next version. Please specify the dataset credentials "
            "explicitly inside the dataset config.".format(DATASET_CREDENTIALS_KEY),
            DeprecationWarning,
        )
        dataset_credentials = credentials.pop(DATASET_CREDENTIALS_KEY)
    else:
        dataset_credentials = deepcopy(credentials)
    return credentials, dataset_credentials