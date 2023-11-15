    def _downloadStream(self, jobStoreFileID, container):
        # The reason this is not in the writer is so we catch non-existant blobs early

        blobProps = container.get_blob_properties(blob_name=jobStoreFileID)

        encrypted = strict_bool(blobProps['x-ms-meta-encrypted'])
        if encrypted and self.keyPath is None:
            raise AssertionError('Content is encrypted but no key was provided.')

        outer_self = self

        class DownloadPipe(ReadablePipe):
            def writeTo(self, writable):
                chunkStart = 0
                fileSize = int(blobProps['Content-Length'])
                while chunkStart < fileSize:
                    chunkEnd = chunkStart + outer_self._maxAzureBlockBytes - 1
                    buf = container.get_blob(blob_name=jobStoreFileID,
                                             x_ms_range="bytes=%d-%d" % (chunkStart, chunkEnd))
                    if encrypted:
                        buf = encryption.decrypt(buf, outer_self.keyPath)
                    writable.write(buf)
                    chunkStart = chunkEnd + 1

        with DownloadPipe() as readable:
            yield readable