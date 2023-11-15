        def downloadStream(self):
            info = self

            class DownloadPipe(ReadablePipe):
                def writeTo(self, writable):
                    if info.content is not None:
                        writable.write(info.content)
                    elif info.version:
                        headers = info._s3EncryptionHeaders()
                        key = info.outer.filesBucket.get_key(info.fileID, validate=False)
                        for attempt in retry_s3():
                            with attempt:
                                key.get_contents_to_file(writable,
                                                         headers=headers,
                                                         version_id=info.version)
                    else:
                        assert False

                    thread = ExceptionalThread(target=writer)
                    thread.start()
                    yield readable
                    thread.join()