        def on_got_metainfo(metainfo):
            if not isinstance(metainfo, dict) or 'info' not in metainfo:
                self._logger.warning("Received metainfo is not a valid dictionary")
                request.setResponseCode(http.INTERNAL_SERVER_ERROR)
                request.write(json.twisted_dumps({"error": 'invalid response'}))
                self.finish_request(request)
                return

            # Add the torrent to GigaChannel as a free-for-all entry, so others can search it
            self.session.lm.mds.TorrentMetadata.add_ffa_from_dict(
                tdef_to_metadata_dict(TorrentDef.load_from_dict(metainfo)))

            # TODO(Martijn): store the stuff in a database!!!
            # TODO(Vadim): this means cache the downloaded torrent in a binary storage, like LevelDB
            infohash = hashlib.sha1(bencode(metainfo['info'])).digest()

            # Check if the torrent is already in the downloads
            metainfo['download_exists'] = infohash in self.session.lm.downloads
            encoded_metainfo = hexlify(json.dumps(metainfo, ensure_ascii=False))

            request.write(json.twisted_dumps({"metainfo": encoded_metainfo}))
            self.finish_request(request)