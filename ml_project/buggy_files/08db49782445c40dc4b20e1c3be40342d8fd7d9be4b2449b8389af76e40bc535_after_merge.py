    def download(self, url, file_path=None, auth=None):
        ret = bytearray()
        response = self.requester.get(url, stream=True, verify=self.verify, auth=auth)
        if not response.ok:
            raise ConanException("Error %d downloading file %s" % (response.status_code, url))

        try:
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                if not file_path:
                    ret += response.content
                else:
                    save(file_path, response.content, append=True)
            else:
                dl = 0
                total_length = int(total_length)
                last_progress = None
                chunk_size = 1024 if not file_path else 1024 * 100
                for data in response.iter_content(chunk_size=chunk_size):
                    dl += len(data)
                    if not file_path:
                        ret.extend(data)
                    else:
                        save(file_path, data, append=True)

                    units = progress_units(dl, total_length)
                    if last_progress != units:  # Avoid screen refresh if nothing has change
                        if self.output:
                            print_progress(self.output, units)
                        last_progress = units
            if not file_path:
                return bytes(ret)
            else:
                return
        except Exception as e:
            logger.debug(e.__class__)
            logger.debug(traceback.format_exc())
            # If this part failed, it means problems with the connection to server
            raise ConanConnectionError("Download failed, check server, possibly try again\n%s"
                                       % str(e))