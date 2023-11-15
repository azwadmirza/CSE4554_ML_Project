    def _set(self, key, value, content_encoding='utf-8', content_type='application/json'):
        gcs_object_key = os.path.join(
            self.prefix,
            self._convert_key_to_filepath(key)
        )

        from google.cloud import storage
        gcs = storage.Client(project=self.project)
        bucket = gcs.get_bucket(self.bucket)
        blob = bucket.blob(gcs_object_key)
        if isinstance(value, str):
            blob.upload_from_string(value.encode(content_encoding), content_encoding=content_encoding,
                                    content_type=content_type)
        else:
            blob.upload_from_string(value, content_type=content_type)
        return gcs_object_key