    def render_GET(self, request):
        """
        .. http:get:: /torrents/(string: torrent infohash)/health

        Fetch the swarm health of a specific torrent. You can optionally specify the timeout to be used in the
        connections to the trackers. This is by default 20 seconds.
        By default, we will not check the health of a torrent again if it was recently checked. You can force a health
        recheck by passing the refresh parameter.

            **Example request**:

            .. sourcecode:: none

                curl http://localhost:8085/torrents/97d2d8f5d37e56cfaeaae151d55f05b077074779/health?timeout=15&refresh=1

            **Example response**:

            .. sourcecode:: javascript

                {
                    "http://mytracker.com:80/announce": [{
                        "seeders": 43,
                        "leechers": 20,
                        "infohash": "97d2d8f5d37e56cfaeaae151d55f05b077074779"
                    }],
                    "http://nonexistingtracker.com:80/announce": {
                        "error": "timeout"
                    }
                }

            :statuscode 404: if the torrent is not found in the database
        """
        timeout = 20
        if 'timeout' in request.args:
            timeout = int(request.args['timeout'][0])

        refresh = False
        if 'refresh' in request.args and len(request.args['refresh']) > 0 and request.args['refresh'][0] == "1":
            refresh = True

        torrent_db_columns = ['C.torrent_id', 'num_seeders', 'num_leechers', 'next_tracker_check']
        torrent_info = self.torrent_db.getTorrent(self.infohash.decode('hex'), torrent_db_columns)

        if torrent_info is None:
            request.setResponseCode(http.NOT_FOUND)
            return json.dumps({"error": "torrent not found in database"})

        def on_health_result(result):
            request.write(json.dumps({'health': result}))
            self.finish_request(request)

        def on_request_error(failure):
            if not request.finished:
                request.setResponseCode(http.BAD_REQUEST)
                request.write(json.dumps({"error": failure.getErrorMessage()}))
            # If the above request.write failed, the request will have already been finished
            if not request.finished:
                self.finish_request(request)

        self.session.check_torrent_health(self.infohash.decode('hex'), timeout=timeout, scrape_now=refresh)\
            .addCallback(on_health_result).addErrback(on_request_error)

        return NOT_DONE_YET