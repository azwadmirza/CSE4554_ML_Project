def merge_ports(md, base, override):
    def parse_sequence_func(seq):
        acc = []
        for item in seq:
            acc.extend(ServicePort.parse(item))
        return to_mapping(acc, 'merge_field')

    field = 'ports'

    if not md.needs_merge(field):
        return

    merged = parse_sequence_func(md.base.get(field, []))
    merged.update(parse_sequence_func(md.override.get(field, [])))
    md[field] = [item for item in sorted(merged.values(), key=lambda x: x.target)]