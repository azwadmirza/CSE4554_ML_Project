    def _downloadStream(self, jobStoreFileID, container):
        # The reason this is not in the writer is so we catch non-existant blobs early

        blobProps = container.get_blob_properties(blob_name=jobStoreFileID)

        encrypted = strict_bool(blobProps['x-ms-meta-encrypted'])
        if encrypted and self.keyPath is None:
            raise AssertionError('Content is encrypted but no key was provided.')

        readable_fh, writable_fh = os.pipe()
        with os.fdopen(readable_fh, 'r') as readable:
            with os.fdopen(writable_fh, 'w') as writable:
                def writer():
                    try:
                        chunkStartPos = 0
                        fileSize = int(blobProps['Content-Length'])
                        while chunkStartPos < fileSize:
                            chunkEndPos = chunkStartPos + self._maxAzureBlockBytes - 1
                            buf = container.get_blob(blob_name=jobStoreFileID,
                                                     x_ms_range="bytes=%d-%d" % (chunkStartPos,
                                                                                 chunkEndPos))
                            if encrypted:
                                buf = encryption.decrypt(buf, self.keyPath)
                            writable.write(buf)
                            chunkStartPos = chunkEndPos + 1
                    finally:
                        # Ensure readers aren't left blocking if this thread crashes.
                        # This close() will send EOF to the reading end and ultimately cause the
                        # yield to return. It also makes the implict .close() done by the enclosing
                        # "with" context redundant but that should be ok since .close() on file
                        # objects are idempotent.
                        writable.close()

                thread = ExceptionalThread(target=writer)
                thread.start()
                yield readable
                thread.join()