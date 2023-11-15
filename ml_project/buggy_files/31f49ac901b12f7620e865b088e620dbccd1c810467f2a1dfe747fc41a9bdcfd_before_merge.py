def match_to_original_specs(str_specs, specs_for_prefix):
    matches_any_spec = lambda dst: next(spc for spc in str_specs if spc.startswith(dst))
    matched_specs_for_prefix = []
    for prefix_with_dists in specs_for_prefix:
        linked = linked_data(prefix_with_dists.prefix)
        r = prefix_with_dists.r
        new_matches = []
        for spec in prefix_with_dists.specs:
            matched = matches_any_spec(spec)
            if matched:
                new_matches.append(matched)
        add_defaults_to_specs(r, linked, new_matches, prefix=prefix_with_dists.prefix)
        matched_specs_for_prefix.append(SpecsForPrefix(
            prefix=prefix_with_dists.prefix, r=prefix_with_dists.r, specs=new_matches))
    return matched_specs_for_prefix