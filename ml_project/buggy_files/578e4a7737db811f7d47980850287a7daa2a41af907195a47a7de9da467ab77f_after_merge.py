def map_params_to_obj(module):
    vrfs = module.params.get('vrfs')
    if not vrfs:
        if not module.params['name'] and module.params['purge']:
            return list()
        elif not module.params['name']:
            module.fail_json(msg='name is required')
        collection = [{'name': module.params['name']}]
    else:
        collection = list()
        for item in vrfs:
            if not isinstance(item, dict):
                collection.append({'name': item})
            elif 'name' not in item:
                module.fail_json(msg='name is required')
            else:
                collection.append(item)

    objects = list()
    for item in collection:
        get_value = partial(get_param_value, item=item, module=module)
        item['description'] = get_value('description')
        item['rd'] = get_value('rd')
        item['interfaces'] = get_value('interfaces')
        item['state'] = get_value('state')
        item['route_import'] = get_value('route_import')
        item['route_export'] = get_value('route_export')
        item['route_both'] = get_value('route_both')
        item['route_import_ipv4'] = get_value('route_import_ipv4')
        item['route_export_ipv4'] = get_value('route_export_ipv4')
        item['route_both_ipv4'] = get_value('route_both_ipv4')
        item['route_import_ipv6'] = get_value('route_import_ipv6')
        item['route_export_ipv6'] = get_value('route_export_ipv6')
        item['route_both_ipv6'] = get_value('route_both_ipv6')
        both_addresses_family = ["", "_ipv6", "_ipv4"]
        for address_family in both_addresses_family:
            if item["route_both%s" % address_family]:
                if not item["route_export%s" % address_family]:
                    item["route_export%s" % address_family] = list()
                if not item["route_import%s" % address_family]:
                    item["route_import%s" % address_family] = list()
                item["route_export%s" % address_family].extend(get_value("route_both%s" % address_family))
                item["route_import%s" % address_family].extend(get_value("route_both%s" % address_family))
        item['associated_interfaces'] = get_value('associated_interfaces')
        objects.append(item)

    return objects