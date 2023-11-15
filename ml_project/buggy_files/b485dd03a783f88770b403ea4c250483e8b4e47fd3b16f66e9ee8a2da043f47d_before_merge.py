    def _downloadStream(self, key, encrypt=True):
        readable_fh, writable_fh = os.pipe()
        with os.fdopen(readable_fh, 'r') as readable:
            with os.fdopen(writable_fh, 'w') as writable:
                def writer():
                    headers = self.encryptedHeaders if encrypt else self.headerValues
                    try:
                        key.get_file(writable, headers=headers)
                    finally:
                        writable.close()

                thread = ExceptionalThread(target=writer)
                thread.start()
                yield readable
                thread.join()