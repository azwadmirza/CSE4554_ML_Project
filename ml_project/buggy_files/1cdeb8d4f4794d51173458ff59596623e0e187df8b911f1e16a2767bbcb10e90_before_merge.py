    def _uploadStream(self, jobStoreFileID, container, checkForModification=False, encrypted=None):
        """
        :param encrypted: True to enforce encryption (will raise exception unless key is set),
        False to prevent encryption or None to encrypt if key is set.
        """
        if checkForModification:
            try:
                expectedVersion = container.get_blob_properties(blob_name=jobStoreFileID)['etag']
            except AzureMissingResourceHttpError:
                expectedVersion = None

        if encrypted is None:
            encrypted = self.keyPath is not None
        elif encrypted:
            if self.keyPath is None:
                raise RuntimeError('Encryption requested but no key was provided')

        maxBlockSize = self._maxAzureBlockBytes
        if encrypted:
            # There is a small overhead for encrypted data.
            maxBlockSize -= encryption.overhead
        readable_fh, writable_fh = os.pipe()
        with os.fdopen(readable_fh, 'r') as readable:
            with os.fdopen(writable_fh, 'w') as writable:
                def reader():
                    blockIDs = []
                    try:
                        while True:
                            buf = readable.read(maxBlockSize)
                            if len(buf) == 0:
                                # We're safe to break here even if we never read anything, since
                                # putting an empty block list creates an empty blob.
                                break
                            if encrypted:
                                buf = encryption.encrypt(buf, self.keyPath)
                            blockID = self._newFileID()
                            container.put_block(blob_name=jobStoreFileID,
                                                block=buf,
                                                blockid=blockID)
                            blockIDs.append(blockID)
                    except:
                        # This is guaranteed to delete any uncommitted
                        # blocks.
                        container.delete_blob(blob_name=jobStoreFileID)
                        raise

                    if checkForModification and expectedVersion is not None:
                        # Acquire a (60-second) write lock,
                        leaseID = container.lease_blob(blob_name=jobStoreFileID,
                                                       x_ms_lease_action='acquire')['x-ms-lease-id']
                        # check for modification,
                        blobProperties = container.get_blob_properties(blob_name=jobStoreFileID)
                        if blobProperties['etag'] != expectedVersion:
                            container.lease_blob(blob_name=jobStoreFileID,
                                                 x_ms_lease_action='release',
                                                 x_ms_lease_id=leaseID)
                            raise ConcurrentFileModificationException(jobStoreFileID)
                        # commit the file,
                        container.put_block_list(blob_name=jobStoreFileID,
                                                 block_list=blockIDs,
                                                 x_ms_lease_id=leaseID,
                                                 x_ms_meta_name_values=dict(
                                                     encrypted=str(encrypted)))
                        # then release the lock.
                        container.lease_blob(blob_name=jobStoreFileID,
                                             x_ms_lease_action='release',
                                             x_ms_lease_id=leaseID)
                    else:
                        # No need to check for modification, just blindly write over whatever
                        # was there.
                        container.put_block_list(blob_name=jobStoreFileID,
                                                 block_list=blockIDs,
                                                 x_ms_meta_name_values=dict(
                                                     encrypted=str(encrypted)))

                thread = ExceptionalThread(target=reader)
                thread.start()
                yield writable
            # The writable is now closed. This will send EOF to the readable and cause that
            # thread to finish.
            thread.join()