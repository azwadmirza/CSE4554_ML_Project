def serialize_config(config, image_digests=None):
    return yaml.safe_dump(
        denormalize_config(config, image_digests),
        default_flow_style=False,
        indent=2,
        width=80,
        allow_unicode=True
    )