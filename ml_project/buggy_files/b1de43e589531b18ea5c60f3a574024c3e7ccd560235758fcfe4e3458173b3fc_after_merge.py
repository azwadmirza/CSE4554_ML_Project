    def _upload(self, from_file, to_info, **_kwargs):
        bucket = self.gs.bucket(to_info.bucket)
        _upload_to_bucket(bucket, from_file)