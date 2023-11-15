    def _uploadStream(self, key, update=False, encrypt=True):
        store = self

        class UploadPipe(WritablePipe):
            def readFrom(self, readable):
                headers = store.encryptedHeaders if encrypt else store.headerValues
                if update:
                    try:
                        key.set_contents_from_stream(readable, headers=headers)
                    except boto.exception.GSDataError:
                        if encrypt:
                            # https://github.com/boto/boto/issues/3518
                            # see self._writeFile for more
                            pass
                        else:
                            raise
                else:
                    try:
                        # The if_generation argument insures that the existing key matches the
                        # given generation, i.e. version, before modifying anything. Passing a
                        # generation of 0 insures that the key does not exist remotely.
                        key.set_contents_from_stream(readable, headers=headers, if_generation=0)
                    except (boto.exception.GSResponseError, boto.exception.GSDataError) as e:
                        if isinstance(e, boto.exception.GSResponseError):
                            if e.status == 412:
                                raise ConcurrentFileModificationException(key.name)
                            else:
                                raise e
                        elif encrypt:
                            # https://github.com/boto/boto/issues/3518
                            # see self._writeFile for more
                            pass
                        else:
                            raise

        with UploadPipe() as writable:
            yield writable