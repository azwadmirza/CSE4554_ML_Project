    def render_PUT(self, request):
        """
        .. http:put:: /downloads

        A PUT request to this endpoint will start a download from a provided URI. This URI can either represent a file
        location, a magnet link or a HTTP(S) url.
        - anon_hops: the number of hops for the anonymous download. 0 hops is equivalent to a plain download
        - safe_seeding: whether the seeding of the download should be anonymous or not (0 = off, 1 = on)
        - destination: the download destination path of the torrent
        - torrent: the URI of the torrent file that should be downloaded. This parameter is required.

            **Example request**:

                .. sourcecode:: none

                    curl -X PUT http://localhost:8085/downloads
                    --data "anon_hops=2&safe_seeding=1&destination=/my/dest/on/disk/&uri=file:/home/me/test.torrent

            **Example response**:

                .. sourcecode:: javascript

                    {"started": True, "infohash": "4344503b7e797ebf31582327a5baae35b11bda01"}
        """
        parameters = http.parse_qs(request.content.read(), 1)

        if 'uri' not in parameters or len(parameters['uri']) == 0:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "uri parameter missing"})

        download_config, error = DownloadsEndpoint.create_dconfig_from_params(parameters)
        if error:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": error})

        def download_added(download):
            request.write(json.dumps({"started": True,
                                      "infohash": download.get_def().get_infohash().encode('hex')}))
            request.finish()

        def on_error(error):
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.write(json.dumps({"error": unichar_string(error.getErrorMessage())}))
            request.finish()

        uri = parameters['uri'][0]
        if uri.startswith("file:"):
            if uri.endswith(".mdblob"):
                filename = url2pathname(uri[5:].encode('utf-8') if isinstance(uri, unicode) else uri[5:])
                try:
                    payload = ChannelMetadataPayload.from_file(filename)
                except IOError:
                    request.setResponseCode(http.BAD_REQUEST)
                    return json.dumps({"error": "file not found"})
                except InvalidSignatureException:
                    request.setResponseCode(http.BAD_REQUEST)
                    return json.dumps({"error": "Metadata has invalid signature"})

                download, _ = self.session.lm.update_channel(payload)
                return json.dumps({"started": True, "infohash": str(download.get_def().get_infohash()).encode('hex')})
            else:
                download_uri = u"file:%s" % url2pathname(uri[5:]).decode('utf-8')
        else:
            download_uri = unquote_plus(unicode(uri, 'utf-8'))
        download_deferred = self.session.start_download_from_uri(download_uri, download_config)
        download_deferred.addCallback(download_added)
        download_deferred.addErrback(on_error)

        return NOT_DONE_YET