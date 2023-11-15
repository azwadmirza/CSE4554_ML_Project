def load_model_from_link(name, **overrides):
    """Load a model from a shortcut link, or directory in spaCy data path."""
    init_file = get_data_path() / name / '__init__.py'
    spec = importlib.util.spec_from_file_location(name, init_file)
    try:
        cls = importlib.util.module_from_spec(spec)
    except AttributeError:
        raise IOError(
            "Cant' load '%s'. If you're using a shortcut link, make sure it "
            "points to a valid model package (not just a data directory)." % name)
    spec.loader.exec_module(cls)
    return cls.load(**overrides)