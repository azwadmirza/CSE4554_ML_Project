def bundle_all_models():
    return bundle_models(Model.model_class_reverse_map.values()) or ""