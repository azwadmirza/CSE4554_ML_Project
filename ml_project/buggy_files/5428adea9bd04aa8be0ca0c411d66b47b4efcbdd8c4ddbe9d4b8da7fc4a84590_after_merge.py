def update_objects(want, have):
    updates = list()
    for entry in want:
        item = next((i for i in have if i['name'] == entry['name']), None)
        if all((item is None, entry['state'] == 'present')):
            updates.append((entry, {}))
        else:
            for key, value in iteritems(entry):
                if value:
                    try:
                        if isinstance(value, list):
                            if sorted(value) != sorted(item[key]):
                                if (entry, item) not in updates:
                                    updates.append((entry, item))
                        elif value != item[key]:
                            if (entry, item) not in updates:
                                updates.append((entry, item))
                    except TypeError:
                        pass
    return updates