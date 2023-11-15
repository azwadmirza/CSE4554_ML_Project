def grafana_delete_datasource(module, data):

    # define http headers
    headers = {'content-type': 'application/json'}
    if 'grafana_api_key' in data and data['grafana_api_key']:
        headers['Authorization'] = "Bearer %s" % data['grafana_api_key']
    else:
        auth = base64.b64encode(to_bytes('%s:%s' % (data['grafana_user'], data['grafana_password'])).replace('\n', ''))
        headers['Authorization'] = 'Basic %s' % auth
        grafana_switch_organisation(module, data['grafana_url'], data['org_id'], headers)

    # test if datasource already exists
    datasource_exists, ds = grafana_datasource_exists(module, data['grafana_url'], data['name'], headers=headers)

    result = {}
    if datasource_exists is True:
        # delete
        r, info = fetch_url(module, '%s/api/datasources/name/%s' % (data['grafana_url'], data['name']), headers=headers, method='DELETE')
        if info['status'] == 200:
            res = json.loads(r.read())
            result['msg'] = "Datasource %s deleted : %s" % (data['name'], res['message'])
            result['changed'] = True
            result['name'] = data['name']
            result['id'] = 0
        else:
            raise GrafanaAPIException('Unable to update the datasource id %s : %s' % (ds['id'], info))
    else:
        # datasource does not exist, do nothing
        result = {'msg': "Datasource %s does not exist." % data['name'],
                  'changed': False,
                  'id': 0,
                  'name': data['name']}

    return result