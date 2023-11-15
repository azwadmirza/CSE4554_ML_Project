    def remove_key(self, key):
        from google.cloud import storage
        from google.cloud.exceptions import NotFound

        gcs = storage.Client(project=self.project)
        bucket = gcs.get_bucket(self.bucket)
        try:
            bucket.delete_blobs(blobs=list(bucket.list_blobs(prefix=self.prefix)))
        except NotFound:
            return False
        return True