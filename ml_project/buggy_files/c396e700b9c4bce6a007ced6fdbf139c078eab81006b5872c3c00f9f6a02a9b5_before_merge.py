    def render_GET(self, request):
        """
        .. http:get:: /downloads?get_peers=(boolean: get_peers)&get_pieces=(boolean: get_pieces)

        A GET request to this endpoint returns all downloads in Tribler, both active and inactive. The progress is a
        number ranging from 0 to 1, indicating the progress of the specific state (downloading, checking etc). The
        download speeds have the unit bytes/sec. The size of the torrent is given in bytes. The estimated time assumed
        is given in seconds. A description of the possible download statuses can be found in the REST API documentation.

        Detailed information about peers and pieces is only requested when the get_peers and/or get_pieces flag is set.
        Note that setting this flag has a negative impact on performance and should only be used in situations
        where this data is required.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/downloads?get_peers=1&get_pieces=1

            **Example response**:

            .. sourcecode:: javascript

                {
                    "downloads": [{
                        "name": "Ubuntu-16.04-desktop-amd64",
                        "progress": 0.31459265,
                        "infohash": "4344503b7e797ebf31582327a5baae35b11bda01",
                        "speed_down": 4938.83,
                        "speed_up": 321.84,
                        "status": "DLSTATUS_DOWNLOADING",
                        "size": 89432483,
                        "eta": 38493,
                        "num_peers": 53,
                        "num_seeds": 93,
                        "total_up": 10000,
                        "total_down": 100000,
                        "ratio": 0.1,
                        "files": [{
                            "index": 0,
                            "name": "ubuntu.iso",
                            "size": 89432483,
                            "included": True
                        }, ...],
                        "trackers": [{
                            "url": "http://ipv6.torrent.ubuntu.com:6969/announce",
                            "status": "Working",
                            "peers": 42
                        }, ...],
                        "hops": 1,
                        "anon_download": True,
                        "safe_seeding": True,
                        "max_upload_speed": 0,
                        "max_download_speed": 0,
                        "destination": "/home/user/file.txt",
                        "availability": 1.234,
                        "peers": [{
                            "ip": "123.456.789.987",
                            "dtotal": 23,
                            "downrate": 0,
                            "uinterested": False,
                            "wstate": "\x00",
                            "optimistic": False,
                            ...
                        }, ...],
                        "total_pieces": 420,
                        "vod_mod": True,
                        "vod_prebuffering_progress": 0.89,
                        "vod_prebuffering_progress_consec": 0.86,
                        "error": "",
                        "time_added": 1484819242,
                    }
                }, ...]
        """
        get_peers = False
        if 'get_peers' in request.args and len(request.args['get_peers']) > 0 \
                and request.args['get_peers'][0] == "1":
            get_peers = True

        get_pieces = False
        if 'get_pieces' in request.args and len(request.args['get_pieces']) > 0 \
                and request.args['get_pieces'][0] == "1":
            get_pieces = True

        get_files = 'get_files' in request.args and request.args['get_files'] and request.args['get_files'][0] == "1"

        downloads_json = []
        downloads = self.session.get_downloads()
        for download in downloads:
            state = download.get_state()
            tdef = download.get_def()

            # Create tracker information of the download
            tracker_info = []
            for url, url_info in download.get_tracker_status().iteritems():
                tracker_info.append({"url": url, "peers": url_info[0], "status": url_info[1]})

            num_seeds, num_peers = state.get_num_seeds_peers()

            download_json = {"name": tdef.get_name(), "progress": state.get_progress(),
                             "infohash": tdef.get_infohash().encode('hex'),
                             "speed_down": state.get_current_speed(DOWNLOAD),
                             "speed_up": state.get_current_speed(UPLOAD),
                             "status": dlstatus_strings[state.get_status()],
                             "size": tdef.get_length(), "eta": state.get_eta(),
                             "num_peers": num_peers, "num_seeds": num_seeds,
                             "total_up": state.get_total_transferred(UPLOAD),
                             "total_down": state.get_total_transferred(DOWNLOAD), "ratio": state.get_seeding_ratio(),
                             "trackers": tracker_info, "hops": download.get_hops(),
                             "anon_download": download.get_anon_mode(), "safe_seeding": download.get_safe_seeding(),
                             # Maximum upload/download rates are set for entire sessions
                             "max_upload_speed": self.session.config.get_libtorrent_max_upload_rate(),
                             "max_download_speed": self.session.config.get_libtorrent_max_download_rate(),
                             "destination": download.get_dest_dir(), "availability": state.get_availability(),
                             "total_pieces": tdef.get_nr_pieces(), "vod_mode": download.get_mode() == DLMODE_VOD,
                             "vod_prebuffering_progress": state.get_vod_prebuffering_progress(),
                             "vod_prebuffering_progress_consec": state.get_vod_prebuffering_progress_consec(),
                             "error": repr(state.get_error()) if state.get_error() else "",
                             "time_added": download.get_time_added(),
                             "credit_mining": download.get_credit_mining()}

            # Add peers information if requested
            if get_peers:
                peer_list = state.get_peerlist()
                for peer_info in peer_list:  # Remove have field since it is very large to transmit.
                    del peer_info['have']
                    if 'extended_version' in peer_info:
                        peer_info['extended_version'] = _safe_extended_peer_info(peer_info['extended_version'])
                    peer_info['id'] = peer_info['id'].encode('hex')

                download_json["peers"] = peer_list

            # Add piece information if requested
            if get_pieces:
                download_json["pieces"] = download.get_pieces_base64()

            # Add files if requested
            if get_files:
                files_completion = dict((name, progress) for name, progress in state.get_files_completion())
                selected_files = download.get_selected_files()
                files_array = []
                file_index = 0
                for fn, size in tdef.get_files_with_length():
                    files_array.append({"index": file_index, "name": fn, "size": size,
                                        "included": (fn in selected_files or not selected_files),
                                        "progress": files_completion.get(fn, 0.0)})
                    file_index += 1

                download_json["files"] = files_array


            downloads_json.append(download_json)
        return json.dumps({"downloads": downloads_json})