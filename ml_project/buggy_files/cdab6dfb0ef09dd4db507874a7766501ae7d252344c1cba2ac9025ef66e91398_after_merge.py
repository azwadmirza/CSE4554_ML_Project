            def generate():
                # Starting a new download
                if not self.web.stay_open:
                    self.download_in_progress = True

                chunk_size = 102400  # 100kb

                fp = open(file_to_download, 'rb')
                self.web.done = False
                canceled = False
                while not self.web.done:
                    # The user has canceled the download, so stop serving the file
                    if not self.web.stop_q.empty():
                        self.web.add_request(self.web.REQUEST_CANCELED, path, {
                            'id': download_id
                        })
                        break

                    chunk = fp.read(chunk_size)
                    if chunk == b'':
                        self.web.done = True
                    else:
                        try:
                            yield chunk

                            # tell GUI the progress
                            downloaded_bytes = fp.tell()
                            percent = (1.0 * downloaded_bytes / self.filesize) * 100

                            # only output to stdout if running onionshare in CLI mode, or if using Linux (#203, #304)
                            if not self.web.is_gui or self.common.platform == 'Linux' or self.common.platform == 'BSD':
                                sys.stdout.write(
                                    "\r{0:s}, {1:.2f}%          ".format(self.common.human_readable_filesize(downloaded_bytes), percent))
                                sys.stdout.flush()

                            self.web.add_request(self.web.REQUEST_PROGRESS, path, {
                                'id': download_id,
                                'bytes': downloaded_bytes
                                })
                            self.web.done = False
                        except:
                            # looks like the download was canceled
                            self.web.done = True
                            canceled = True

                            # tell the GUI the download has canceled
                            self.web.add_request(self.web.REQUEST_CANCELED, path, {
                                'id': download_id
                            })

                fp.close()

                if self.common.platform != 'Darwin':
                    sys.stdout.write("\n")

                # Download is finished
                if not self.web.stay_open:
                    self.download_in_progress = False

                # Close the server, if necessary
                if not self.web.stay_open and not canceled:
                    print(strings._("closing_automatically"))
                    self.web.running = False
                    try:
                        if shutdown_func is None:
                            raise RuntimeError('Not running with the Werkzeug Server')
                        shutdown_func()
                    except:
                        pass