def get_diff(w, obj):
    c = deepcopy(w)
    entries = ('interfaces', 'associated_interfaces', 'name', 'delay', 'vlan_range')
    for key in entries:
        if key in c:
            del c[key]

    o = deepcopy(obj)
    del o['interfaces']
    del o['name']
    if o['vlan_id'] == w['vlan_id']:
        diff_dict = dict(set(c.items()) - set(o.items()))
        return diff_dict