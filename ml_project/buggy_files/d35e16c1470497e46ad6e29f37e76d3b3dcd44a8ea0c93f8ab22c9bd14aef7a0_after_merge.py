def bundle_all_models():
    key = calc_cache_key()
    bundle = _bundle_cache.get(key, None)
    if bundle is None:
        _bundle_cache[key] = bundle = bundle_models(Model.model_class_reverse_map.values()) or ""
    return bundle