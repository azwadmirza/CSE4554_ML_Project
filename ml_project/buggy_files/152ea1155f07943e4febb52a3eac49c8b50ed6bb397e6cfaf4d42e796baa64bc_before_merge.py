def get_model_by_path(schema: Dict[str, Any], keys: List[str]) -> Dict:
    if len(keys) == 1:
        return schema[keys[0]]
    return get_model_by_path(schema[keys[0]], keys[1:])