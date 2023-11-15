    def _uploadStream(self, key, update=False, encrypt=True):
        readable_fh, writable_fh = os.pipe()
        with os.fdopen(readable_fh, 'r') as readable:
            with os.fdopen(writable_fh, 'w') as writable:
                def writer():
                    headers = self.encryptedHeaders if encrypt else self.headerValues
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
                            # The if_condition kwarg insures that the existing key matches given
                            # generation (version) before modifying anything. Setting
                            # if_generation=0 insures key does not exist remotely
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
                thread = ExceptionalThread(target=writer)
                thread.start()
                yield writable
            thread.join()