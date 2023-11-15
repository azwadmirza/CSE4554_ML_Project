def map_params_to_obj(module):
    obj = []

    if 'aggregate' in module.params and module.params['aggregate']:
        args = {'dest': '',
                'remote_server': '',
                'name': '',
                'facility': '',
                'dest_level': '',
                'facility_level': ''}

        for c in module.params['aggregate']:
            d = c.copy()

            for key in args:
                if key not in d:
                    d[key] = None

            if d['dest_level'] is not None:
                d['dest_level'] = str(d['dest_level'])

            if d['facility_level'] is not None:
                d['facility_level'] = str(d['facility_level'])

            if 'state' not in d:
                d['state'] = module.params['state']

            obj.append(d)

    else:
        dest_level = None
        facility_level = None

        if module.params['dest_level'] is not None:
            dest_level = str(module.params['dest_level'])

        if module.params['facility_level'] is not None:
            facility_level = str(module.params['facility_level'])

        obj.append({
            'dest': module.params['dest'],
            'remote_server': module.params['remote_server'],
            'name': module.params['name'],
            'facility': module.params['facility'],
            'dest_level': dest_level,
            'facility_level': facility_level,
            'state': module.params['state']
        })
    return obj