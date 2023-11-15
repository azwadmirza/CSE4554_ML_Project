def get_diff(w, have):
    c = deepcopy(w)
    del c['interfaces']
    del c['name']
    del c['associated_interfaces']
    for o in have:
        del o['interfaces']
        del o['name']
        if o['vlan_id'] == w['vlan_id']:
            diff_dict = dict(set(c.items()) - set(o.items()))
            return diff_dict