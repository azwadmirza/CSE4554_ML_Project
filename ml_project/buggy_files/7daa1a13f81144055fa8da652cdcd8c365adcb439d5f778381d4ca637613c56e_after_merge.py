def transform_account_list(result):
    transformed = []
    for r in result:
        res = OrderedDict([('Name', r['name']),
                           ('CloudName', r['cloudName']),
                           ('SubscriptionId', r['id']),
                           ('State', r.get('state')),
                           ('IsDefault', r['isDefault'])])
        transformed.append(res)
    return transformed