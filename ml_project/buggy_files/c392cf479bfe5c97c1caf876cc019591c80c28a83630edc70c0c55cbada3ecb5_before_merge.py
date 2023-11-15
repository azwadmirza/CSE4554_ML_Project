        def downloadStream(self):
            readable_fh, writable_fh = os.pipe()
            with os.fdopen(readable_fh, 'r') as readable:
                with os.fdopen(writable_fh, 'w') as writable:
                    def writer():
                        try:
                            if self.content is not None:
                                writable.write(self.content)
                            elif self.version:
                                headers = self._s3EncryptionHeaders()
                                key = self.outer.filesBucket.get_key(self.fileID, validate=False)
                                for attempt in retry_s3():
                                    with attempt:
                                        key.get_contents_to_file(writable,
                                                                 headers=headers,
                                                                 version_id=self.version)
                            else:
                                assert False
                        finally:
                            # This close() will send EOF to the reading end and ultimately cause
                            # the yield to return. It also makes the implict .close() done by the
                            #  enclosing "with" context redundant but that should be ok since
                            # .close() on file objects are idempotent.
                            writable.close()

                    thread = ExceptionalThread(target=writer)
                    thread.start()
                    yield readable
                    thread.join()