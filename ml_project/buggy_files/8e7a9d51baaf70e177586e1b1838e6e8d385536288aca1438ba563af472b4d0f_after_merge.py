        def _on_torrent_created(result):
            """
            Success callback
            :param result: from create_torrent_file
            """
            metainfo_dict = bdecode_compat(result['metainfo'])

            if export_dir and os.path.exists(export_dir):
                save_path = os.path.join(export_dir, "%s.torrent" % name)
                with open(save_path, "wb") as fd:
                    fd.write(result['metainfo'])

            # Download this torrent if specified
            if 'download' in args and args['download'] and args['download'][0] == "1":
                download_config = DownloadConfig()
                download_config.set_dest_dir(result['base_path'] if len(file_path_list) == 1 else result['base_dir'])
                try:
                    self.session.lm.ltmgr.start_download(
                        tdef=TorrentDef(metainfo=metainfo_dict), dconfig=download_config)
                except DuplicateDownloadException:
                    self._logger.warning("The created torrent is already being downloaded.")

            request.write(json.twisted_dumps({"torrent": base64.b64encode(result['metainfo']).decode('utf-8')}))
            # If the above request.write failed, the request will have already been finished
            if not request.finished:
                request.finish()