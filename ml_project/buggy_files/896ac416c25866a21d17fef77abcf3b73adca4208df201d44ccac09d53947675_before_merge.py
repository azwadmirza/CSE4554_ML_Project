def load_model_from_path(model_path, meta=False, **overrides):
    """Load a model from a data directory path. Creates Language class with
    pipeline from meta.json and then calls from_disk() with path."""
    if not meta:
        meta = get_model_meta(model_path)
    # Support language factories registered via entry points (e.g. custom
    # language subclass) while keeping top-level language identifier "lang"
    lang = meta.get("lang_factory", meta["lang"])
    cls = get_lang_class(lang)
    nlp = cls(meta=meta, **overrides)
    pipeline = meta.get("pipeline", [])
    factories = meta.get("factories", {})
    disable = overrides.get("disable", [])
    if pipeline is True:
        pipeline = nlp.Defaults.pipe_names
    elif pipeline in (False, None):
        pipeline = []
    for name in pipeline:
        if name not in disable:
            config = meta.get("pipeline_args", {}).get(name, {})
            config.update(overrides)
            factory = factories.get(name, name)
            component = nlp.create_pipe(factory, config=config)
            nlp.add_pipe(component, name=name)
    return nlp.from_disk(model_path, exclude=disable)