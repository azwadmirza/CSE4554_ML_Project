def parse_both(configobj, name, address_family='global'):
    rd_pattern = re.compile('(?P<rd>.+:.+)')
    matches = list()
    export_match = None
    import_match = None
    if address_family == "global":
        export_match = parse_export(configobj, name)
        import_match = parse_import(configobj, name)
    elif address_family == "ipv4":
        export_match = parse_export_ipv4(configobj, name)
        import_match = parse_import_ipv4(configobj, name)
    elif address_family == "ipv6":
        export_match = parse_export_ipv6(configobj, name)
        import_match = parse_import_ipv6(configobj, name)
    if import_match and export_match:
        for ex in export_match:
            exrd = rd_pattern.search(ex)
            exrd = exrd.groupdict().get('rd')
            for im in import_match:
                imrd = rd_pattern.search(im)
                imrd = imrd.groupdict().get('rd')
                if exrd == imrd:
                    matches.extend([exrd]) if exrd not in matches else None
                    matches.extend([imrd]) if imrd not in matches else None
    return matches