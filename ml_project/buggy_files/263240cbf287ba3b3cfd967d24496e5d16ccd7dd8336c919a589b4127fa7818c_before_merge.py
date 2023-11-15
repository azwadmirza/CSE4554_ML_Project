        def uploadStream(self, multipart=True, allowInlining=True):
            store = self.outer
            readable_fh, writable_fh = os.pipe()
            with os.fdopen(readable_fh, 'r') as readable:
                with os.fdopen(writable_fh, 'w') as writable:
                    def multipartReader():
                        buf = readable.read(store.partSize)
                        if allowInlining and len(buf) <= self._maxInlinedSize():
                            self.content = buf
                        else:
                            headers = self._s3EncryptionHeaders()
                            for attempt in retry_s3():
                                with attempt:
                                    upload = store.filesBucket.initiate_multipart_upload(
                                        key_name=self.fileID,
                                        headers=headers)
                            try:
                                for part_num in itertools.count():
                                    # There must be at least one part, even if the file is empty.
                                    if len(buf) == 0 and part_num > 0:
                                        break
                                    for attempt in retry_s3():
                                        with attempt:
                                            upload.upload_part_from_file(fp=StringIO(buf),
                                                                         # part numbers are 1-based
                                                                         part_num=part_num + 1,
                                                                         headers=headers)
                                    if len(buf) == 0:
                                        break
                                    buf = readable.read(self.outer.partSize)
                            except:
                                with panic(log=log):
                                    for attempt in retry_s3():
                                        with attempt:
                                            upload.cancel_upload()
                            else:
                                for attempt in retry_s3():
                                    with attempt:
                                        self.version = upload.complete_upload().version_id

                    def reader():
                        buf = readable.read()
                        if allowInlining and len(buf) <= self._maxInlinedSize():
                            self.content = buf
                        else:
                            key = store.filesBucket.new_key(key_name=self.fileID)
                            buf = StringIO(buf)
                            headers = self._s3EncryptionHeaders()
                            for attempt in retry_s3():
                                with attempt:
                                    assert buf.len == key.set_contents_from_file(fp=buf,
                                                                                 headers=headers)
                            self.version = key.version_id

                    thread = ExceptionalThread(target=multipartReader if multipart else reader)
                    thread.start()
                    yield writable
                # The writable is now closed. This will send EOF to the readable and cause that
                # thread to finish.
                thread.join()
                assert bool(self.version) == (self.content is None)