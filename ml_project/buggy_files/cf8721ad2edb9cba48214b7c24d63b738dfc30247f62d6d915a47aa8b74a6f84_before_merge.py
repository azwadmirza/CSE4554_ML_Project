def _xml_replace(query, targets, parent_map):
    # parent_el = query.find('..') ## Something like this would be better with newer xml library
    parent_el = parent_map[query]
    matching_index = -1
    # for index, el in enumerate(parent_el.iter('.')):  ## Something like this for newer implementation
    for index, el in enumerate(list(parent_el)):
        if el == query:
            matching_index = index
            break
    assert matching_index >= 0
    current_index = matching_index
    for target in targets:
        current_index += 1
        parent_el.insert(current_index, target)
    parent_el.remove(query)