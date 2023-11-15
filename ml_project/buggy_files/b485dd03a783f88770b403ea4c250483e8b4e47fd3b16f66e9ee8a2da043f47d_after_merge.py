    def _downloadStream(self, key, encrypt=True):
        store = self

        class DownloadPipe(ReadablePipe):
            def writeTo(self, writable):
                headers = store.encryptedHeaders if encrypt else store.headerValues
                try:
                    key.get_file(writable, headers=headers)
                finally:
                    writable.close()

        with DownloadPipe() as readable:
            yield readable