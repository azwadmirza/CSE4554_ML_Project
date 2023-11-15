def _expand_yield_statements(macro_def, expand_el):
    yield_els = [yield_el for macro_def_el in macro_def for yield_el in macro_def_el.findall('.//yield')]

    expand_el_children = list(expand_el)
    macro_def_parent_map = \
        dict((c, p) for macro_def_el in macro_def for p in macro_def_el.iter() for c in p)

    for yield_el in yield_els:
        _xml_replace(yield_el, expand_el_children, macro_def_parent_map)

    # Replace yields at the top level of a macro, seems hacky approach
    replace_yield = True
    while replace_yield:
        for i, macro_def_el in enumerate(macro_def):
            if macro_def_el.tag == "yield":
                for target in expand_el_children:
                    i += 1
                    macro_def.insert(i, target)
                macro_def.remove(macro_def_el)
                continue

        replace_yield = False