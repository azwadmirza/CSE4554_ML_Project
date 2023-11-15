    def entry_complete(self, e, task=None):
        if not e.accepted:
            log.warning('Not removing %s entry %s', e.state, e['title'])
        elif 'remove_url' not in e:
            log.warning('No remove_url for %s, skipping', e['title'])
        elif task.options.test:
            log.info('Would remove from watchlist: %s', e['title'])
        else:
            log.info('Removing from watchlist: %s', e['title'])

            headers = {
                'Origin': 'https://www.npo.nl',
                'Referer': 'https://www.npo.nl/mijn_npo',
                'X-XSRF-TOKEN': requests.cookies['XSRF-TOKEN'],
                'X-Requested-With': 'XMLHttpRequest'
            }

            try:
                delete_response = requests.post(e['remove_url'], headers=headers, cookies=requests.cookies)
            except HTTPError as error:
                log.error('Failed to remove %s, got status %s', e['title'], error.response.status_code)
            else:
                if delete_response.status_code != requests.codes.ok:
                    log.warning('Failed to remove %s, got status %s', e['title'], delete_response.status_code)