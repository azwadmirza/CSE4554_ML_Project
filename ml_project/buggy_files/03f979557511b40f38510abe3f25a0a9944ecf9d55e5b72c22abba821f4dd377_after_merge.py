    def _update_library(self, host=None, series_name=None):
        """Handle updating KODI host via HTTP JSON-RPC.

        Attempts to update the KODI video library for a specific tv show if passed,
        otherwise update the whole library if enabled.

        Args:
            host: KODI webserver host:port
            series_name: Name of a TV show to specifically target the library update for

        Returns:
            Returns True or False

        """
        if not host:
            log.warning(u'No KODI host passed, aborting update')
            return False

        log.info(u'Updating KODI library via JSON method for host: {0}', host)

        # if we're doing per-show
        if series_name:
            series_name = unquote_plus(series_name)
            tvshowid = -1
            path = ''

            log.debug(u'Updating library in KODI via JSON method for show {0}', series_name)

            # let's try letting kodi filter the shows
            shows_command = {
                'jsonrpc': '2.0',
                'method': 'VideoLibrary.GetTVShows',
                'params': {
                    'filter': {
                        'field': 'title',
                        'operator': 'is',
                        'value': series_name,
                    },
                    'properties': ['title'],
                },
                'id': 'Medusa',
            }

            # get tvshowid by series_name
            series_response = self._send_to_kodi(shows_command, host)

            if series_response and 'result' in series_response and 'tvshows' in series_response['result']:
                shows = series_response['result']['tvshows']
            else:
                # fall back to retrieving the entire show list
                shows_command = {
                    'jsonrpc': '2.0',
                    'method': 'VideoLibrary.GetTVShows',
                    'id': 1,
                }
                series_response = self._send_to_kodi(shows_command, host)

                if series_response and 'result' in series_response and 'tvshows' in series_response['result']:
                    shows = series_response['result']['tvshows']
                else:
                    log.debug(u'KODI: No tvshows in KODI TV show list')
                    return False

            for show in shows:
                if ('label' in show and show['label'] == series_name) or ('title' in show and show['title'] == series_name):
                    tvshowid = show['tvshowid']
                    # set the path is we have it already
                    if 'file' in show:
                        path = show['file']

                    break

            # this can be big, so free some memory
            del shows

            # we didn't find the show (exact match), thus revert to just doing a full update if enabled
            if tvshowid == -1:
                log.debug(u'Exact show name not matched in KODI TV show list')
                return False

            # lookup tv-show path if we don't already know it
            if not path:
                path_command = {
                    'jsonrpc': '2.0',
                    'method': 'VideoLibrary.GetTVShowDetails',
                    'params': {
                        'tvshowid': tvshowid,
                        'properties': ['file'],
                    },
                    'id': 1,
                }
                path_response = self._send_to_kodi(path_command, host)

                path = path_response['result']['tvshowdetails']['file']

            log.debug(u'Received Show: {0} with ID: {1} Path: {2}', series_name, tvshowid, path)

            if not path:
                log.warning(u'No valid path found for {0} with ID: {1} on {2}', series_name, tvshowid, host)
                return False

            log.debug(u'KODI Updating {0} on {1} at {2}', series_name, host, path)
            update_command = {
                'jsonrpc': '2.0',
                'method': 'VideoLibrary.Scan',
                'params': {
                    'directory': path,
                },
                'id': 1,
            }
            request = self._send_to_kodi(update_command, host)
            if not request:
                log.warning(u'Update of show directory failed on {0} on {1} at {2}', series_name, host, path)
                return False

            # catch if there was an error in the returned request
            for r in request:
                if 'error' in r:
                    log.warning(u'Error while attempting to update show directory for {0} on {1} at {2} ',
                                series_name, host, path)
                    return False

        # do a full update if requested
        else:
            log.debug(u'Doing Full Library KODI update on host: {0}', host)
            update_command = {
                'jsonrpc': '2.0',
                'method': 'VideoLibrary.Scan',
                'id': 1,
            }
            request = self._send_to_kodi(update_command, host)

            if not request:
                log.warning(u'KODI Full Library update failed on: {0}', host)
                return False

        return True