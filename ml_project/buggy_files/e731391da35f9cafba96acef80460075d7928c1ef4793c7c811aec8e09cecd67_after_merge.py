def grafana_create_dashboard(module, data):

    # define data payload for grafana API
    try:
        with open(data['path'], 'r') as json_file:
            payload = json.load(json_file)
    except Exception as e:
        raise GrafanaAPIException("Can't load json file %s" % to_native(e))

    # Check that the dashboard JSON is nested under the 'dashboard' key
    if 'dashboard' not in payload:
        payload = {'dashboard': payload}

    # define http header
    headers = grafana_headers(module, data)

    grafana_version = get_grafana_version(module, data['grafana_url'], headers)
    if grafana_version < 5:
        if data.get('slug'):
            uid = data['slug']
        elif 'meta' in payload and 'slug' in payload['meta']:
            uid = payload['meta']['slug']
        else:
            raise GrafanaMalformedJson('No slug found in json. Needed with grafana < 5')
    else:
        if data.get('uid'):
            uid = data['uid']
        elif 'uid' in payload['dashboard']:
            uid = payload['dashboard']['uid']
        else:
            uid = None

    result = {}

    # test if the folder exists
    if grafana_version >= 5:
        folder_exists, folder_id = grafana_folder_exists(module, data['grafana_url'], data['folder'], headers)
        if folder_exists is False:
            result['msg'] = "Dashboard folder '%s' does not exist." % data['folder']
            result['uid'] = uid
            result['changed'] = False
            return result

        payload['folderId'] = folder_id

    # test if dashboard already exists
    if uid:
        dashboard_exists, dashboard = grafana_dashboard_exists(
            module, data['grafana_url'], uid, headers=headers)
    else:
        dashboard_exists, dashboard = grafana_dashboard_search(
            module, data['grafana_url'], folder_id, payload['dashboard']['title'], headers=headers)

    if dashboard_exists is True:
        if grafana_dashboard_changed(payload, dashboard):
            # update
            if 'overwrite' in data and data['overwrite']:
                payload['overwrite'] = True
            if 'commit_message' in data and data['commit_message']:
                payload['message'] = data['commit_message']

            r, info = fetch_url(module, '%s/api/dashboards/db' % data['grafana_url'],
                                data=json.dumps(payload), headers=headers, method='POST')
            if info['status'] == 200:
                if grafana_version >= 5:
                    try:
                        dashboard = json.loads(r.read())
                        uid = dashboard['uid']
                    except Exception as e:
                        raise GrafanaAPIException(e)
                result['uid'] = uid
                result['msg'] = "Dashboard %s updated" % payload['dashboard']['title']
                result['changed'] = True
            else:
                body = json.loads(info['body'])
                raise GrafanaAPIException('Unable to update the dashboard %s : %s (HTTP: %d)' %
                                          (uid, body['commit_message'], info['status']))
        else:
            # unchanged
            result['uid'] = uid
            result['msg'] = "Dashboard %s unchanged." % payload['dashboard']['title']
            result['changed'] = False
    else:
        # create
        if folder_exists is True:
            payload['folderId'] = folder_id

        r, info = fetch_url(module, '%s/api/dashboards/db' % data['grafana_url'],
                            data=json.dumps(payload), headers=headers, method='POST')
        if info['status'] == 200:
            result['msg'] = "Dashboard %s created" % payload['dashboard']['title']
            result['changed'] = True
            if grafana_version >= 5:
                try:
                    dashboard = json.loads(r.read())
                    uid = dashboard['uid']
                except Exception as e:
                    raise GrafanaAPIException(e)
            result['uid'] = uid
        else:
            raise GrafanaAPIException('Unable to create the new dashboard %s : %s - %s.' %
                                      (payload['dashboard']['title'], info['status'], info))

    return result