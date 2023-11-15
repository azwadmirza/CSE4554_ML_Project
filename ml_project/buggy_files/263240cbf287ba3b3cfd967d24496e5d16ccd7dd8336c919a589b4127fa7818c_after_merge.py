        def uploadStream(self, multipart=True, allowInlining=True):
            info = self
            store = self.outer

            class MultiPartPipe(WritablePipe):
                def readFrom(self, readable):
                    buf = readable.read(store.partSize)
                    if allowInlining and len(buf) <= info._maxInlinedSize():
                        info.content = buf
                    else:
                        headers = info._s3EncryptionHeaders()
                        for attempt in retry_s3():
                            with attempt:
                                upload = store.filesBucket.initiate_multipart_upload(
                                    key_name=info.fileID,
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
                                buf = readable.read(info.outer.partSize)
                        except:
                            with panic(log=log):
                                for attempt in retry_s3():
                                    with attempt:
                                        upload.cancel_upload()
                        else:
                            for attempt in retry_s3():
                                with attempt:
                                    info.version = upload.complete_upload().version_id

            class SinglePartPipe(WritablePipe):
                def readFrom(self, readable):
                    buf = readable.read()
                    if allowInlining and len(buf) <= info._maxInlinedSize():
                        info.content = buf
                    else:
                        key = store.filesBucket.new_key(key_name=info.fileID)
                        buf = StringIO(buf)
                        headers = info._s3EncryptionHeaders()
                        for attempt in retry_s3():
                            with attempt:
                                assert buf.len == key.set_contents_from_file(fp=buf,
                                                                             headers=headers)
                        info.version = key.version_id

            with MultiPartPipe() if multipart else SinglePartPipe() as writable:
                yield writable

            assert bool(self.version) == (self.content is None)