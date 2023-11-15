def _split_credentials(
    credentials: Union[Dict[str, Any], None]
) -> Tuple[Dict[str, Any], Any]:
    credentials = deepcopy(credentials) or {}
    dataset_credentials = credentials.pop(
        DATASET_CREDENTIALS_KEY, deepcopy(credentials)
    )
    return credentials, dataset_credentials