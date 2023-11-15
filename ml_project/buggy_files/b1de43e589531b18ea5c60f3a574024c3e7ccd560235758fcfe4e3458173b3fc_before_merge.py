    def _upload(self, from_file, to_info, **_kwargs):
        bucket = self.gs.bucket(to_info.bucket)
        blob = bucket.blob(to_info.path)
        blob.upload_from_filename(from_file)