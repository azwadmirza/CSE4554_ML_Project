def parse_both(configobj, name):
    matches = list()
    export_match = parse_export(configobj, name)
    import_match = parse_import(configobj, name)
    matches.extend(export_match)
    matches.extend(import_match)
    return matches