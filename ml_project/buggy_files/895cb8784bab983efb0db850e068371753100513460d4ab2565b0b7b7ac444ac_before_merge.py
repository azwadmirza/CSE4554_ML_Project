def log_variant(log_file, variant_data):
    mkdir_p(os.path.dirname(log_file))
    if hasattr(variant_data, "dump"):
        variant_data = variant_data.dump()
    variant_json = stub_to_json(variant_data)
    with open(log_file, "w") as f:
        json.dump(variant_json, f, indent=2, sort_keys=True, cls=MyEncoder)