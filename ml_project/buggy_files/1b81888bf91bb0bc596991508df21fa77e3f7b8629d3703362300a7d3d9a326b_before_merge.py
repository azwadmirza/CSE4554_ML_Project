def generate_meta(model_path, existing_meta, msg):
    meta = existing_meta or {}
    settings = [
        ("lang", "Model language", meta.get("lang", "en")),
        ("name", "Model name", meta.get("name", "model")),
        ("version", "Model version", meta.get("version", "0.0.0")),
        ("spacy_version", "Required spaCy version", ">=%s,<3.0.0" % about.__version__),
        ("description", "Model description", meta.get("description", False)),
        ("author", "Author", meta.get("author", False)),
        ("email", "Author email", meta.get("email", False)),
        ("url", "Author website", meta.get("url", False)),
        ("license", "License", meta.get("license", "CC BY-SA 3.0")),
    ]
    nlp = util.load_model_from_path(Path(model_path))
    meta["pipeline"] = nlp.pipe_names
    meta["vectors"] = {
        "width": nlp.vocab.vectors_length,
        "vectors": len(nlp.vocab.vectors),
        "keys": nlp.vocab.vectors.n_keys,
    }
    msg.divider("Generating meta.json")
    msg.text(
        "Enter the package settings for your model. The following information "
        "will be read from your model data: pipeline, vectors."
    )
    for setting, desc, default in settings:
        response = get_raw_input(desc, default)
        meta[setting] = default if response == "" and default else response
    if about.__title__ != "spacy":
        meta["parent_package"] = about.__title__
    return meta