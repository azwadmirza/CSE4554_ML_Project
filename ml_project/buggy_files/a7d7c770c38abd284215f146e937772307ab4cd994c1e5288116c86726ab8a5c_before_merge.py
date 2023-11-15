        def _on_torrent_created(result):
            """
            Success callback
            :param result: from create_torrent_file
            """
            with open(result['torrent_file_path'], 'rb') as f:
                torrent_64 = base64.b64encode(f.read())

            # Download this torrent if specified
            if 'download' in request.args and len(request.args['download']) > 0 \
                    and request.args['download'][0] == "1":
                download_config = DownloadStartupConfig()
                download_config.set_dest_dir(result['base_path'])
                try:
                    self.session.start_download_from_uri('file:' + result['torrent_file_path'], download_config)
                except DuplicateDownloadException:
                    self._logger.warning("The created torrent is already being downloaded.")

            request.write(json.dumps({"torrent": torrent_64}))
            request.finish()