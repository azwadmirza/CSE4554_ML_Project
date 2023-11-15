def get_update_status():
    status = {
        'update': False,
        'success': False,
        'message': '',
        'current_commit_hash': ''
    }
    parents = []

    repository_url = 'https://api.github.com/repos/janeczku/calibre-web'
    tz = datetime.timedelta(seconds=time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)

    if request.method == "GET":
        version = helper.get_current_version_info()
        if version is False:
            status['current_commit_hash'] = _(u'Unknown')
        else:
            status['current_commit_hash'] = version['hash']

        try:
            r = requests.get(repository_url + '/git/refs/heads/master')
            r.raise_for_status()
            commit = r.json()
        except requests.exceptions.HTTPError as ex:
            status['message'] = _(u'HTTP Error') + ' ' + str(ex)
        except requests.exceptions.ConnectionError:
            status['message'] = _(u'Connection error')
        except requests.exceptions.Timeout:
            status['message'] = _(u'Timeout while establishing connection')
        except requests.exceptions.RequestException:
            status['message'] = _(u'General error')

        if status['message'] != '':
            return json.dumps(status)

        if 'object' not in commit:
            status['message'] = _(u'Unexpected data while reading update information')
            return json.dumps(status)

        if commit['object']['sha'] == status['current_commit_hash']:
            status.update({
                'update': False,
                'success': True,
                'message': _(u'No update available. You already have the latest version installed')
            })
            return json.dumps(status)

        # a new update is available
        status['update'] = True

        try:
            r = requests.get(repository_url + '/git/commits/' + commit['object']['sha'])
            r.raise_for_status()
            update_data = r.json()
        except requests.exceptions.HTTPError as ex:
            status['error'] = _(u'HTTP Error') + ' ' + str(ex)
        except requests.exceptions.ConnectionError:
            status['error'] = _(u'Connection error')
        except requests.exceptions.Timeout:
            status['error'] = _(u'Timeout while establishing connection')
        except requests.exceptions.RequestException:
            status['error'] = _(u'General error')

        if status['message'] != '':
            return json.dumps(status)

        if 'committer' in update_data and 'message' in update_data:
            status['success'] = True
            status['message'] = _(u'A new update is available. Click on the button below to update to the latest version.')

            new_commit_date = datetime.datetime.strptime(
                update_data['committer']['date'], '%Y-%m-%dT%H:%M:%SZ') - tz
            parents.append(
                [
                    format_datetime(new_commit_date, format='short', locale=get_locale()),
                    update_data['message'],
                    update_data['sha']
                ]
            )

            # it only makes sense to analyze the parents if we know the current commit hash
            if status['current_commit_hash'] != '':
                try:
                    parent_commit = update_data['parents'][0]
                    # limit the maximum search depth
                    remaining_parents_cnt = 10
                except IndexError:
                    remaining_parents_cnt = None

                if remaining_parents_cnt is not None:
                    while True:
                        if remaining_parents_cnt == 0:
                            break

                        # check if we are more than one update behind if so, go up the tree
                        if parent_commit['sha'] != status['current_commit_hash']:
                            try:
                                r = requests.get(parent_commit['url'])
                                r.raise_for_status()
                                parent_data = r.json()

                                parent_commit_date = datetime.datetime.strptime(
                                    parent_data['committer']['date'], '%Y-%m-%dT%H:%M:%SZ') - tz
                                parent_commit_date = format_datetime(
                                    parent_commit_date, format='short', locale=get_locale())

                                parents.append([parent_commit_date, parent_data['message'], parent_data['sha']])
                                parent_commit = parent_data['parents'][0]
                                remaining_parents_cnt -= 1
                            except Exception:
                                # it isn't crucial if we can't get information about the parent
                                break
                        else:
                            # parent is our current version
                            break

        else:
            status['success'] = False
            status['message'] = _(u'Could not fetch update information')

    status['history'] = parents
    return json.dumps(status)